from datetime import UTC, datetime
from secrets import token_urlsafe
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import VALID_GAME_MODES, WINS_TO_VICTORY
from app.core.enums import BattleStatus
from app.core.exceptions import BattleError
from app.core.logging import logger
from app.integrations.opendota import opendota_client
from app.models import BattleMatchEvent, User
from app.models.battle import Battle


class BattleService:

    @staticmethod
    async def create_battle(db: AsyncSession, creator_user: User) -> Battle:
        token = token_urlsafe(16)

        battle = Battle(
            creator_id=creator_user.id,
            invite_token=token,
            status=BattleStatus.pending.value
        )

        db.add(battle)
        await db.commit()
        await db.refresh(battle)

        return battle

    @staticmethod
    async def accept_battle(db: AsyncSession, battle: Battle, user: User) -> Battle:
        if battle.status != BattleStatus.pending.value:
            raise BattleError(status_code=409, message="Батл уже играется или завершен.")

        if battle.creator_id == user.id:
            raise BattleError(status_code=400, message="Нельзя принять свой же батл.")

        battle.opponent_id = user.id
        battle.status = BattleStatus.active.value
        battle.starts_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(battle)

        return battle

    @staticmethod
    async def decline_battle(db: AsyncSession, battle: Battle, user: User) -> Battle:
        if battle.status != BattleStatus.pending.value:
            raise BattleError(status_code=409, message="Батл уже играется или завершен.")

        if battle.creator_id == user.id:
            raise BattleError(
                status_code=400,
                message="Создатель не может отклонить свой батл. Используйте отмену."
            )

        if battle.opponent_id != user.id:
            raise BattleError(status_code=403, message="Вы не участник этого батла.")

        battle.status = BattleStatus.cancelled.value
        battle.finished_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(battle)

        return battle

    @staticmethod
    async def cancel_battle(db: AsyncSession, battle: Battle, user: User) -> Any:
        if battle.status not in (BattleStatus.pending.value, BattleStatus.active.value):
            raise BattleError(status_code=409, message="Нельзя отменить баттл в текущем статусе.")

        if battle.creator_id != user.id:
            raise BattleError(status_code=400, message="Только создатель может отменить батл.")

        battle.status = BattleStatus.cancelled.value
        battle.finished_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(battle)

        return battle

    @staticmethod
    async def get_user_battles(db: AsyncSession, user: User) -> list[Battle]:
        return (
            await db.scalars(
                select(Battle)
                .where(
                    or_(Battle.creator_id == user.id, Battle.opponent_id == user.id)
                )
            )
        ).all()

    @staticmethod
    async def poll_battle(db: AsyncSession, redis, battle: Battle) -> Any:
        if battle.status != BattleStatus.active.value:
            return

        locked = await redis.setnx(f"polling:{battle.id}", "1")
        if not locked:
            return
        await redis.expire(f"polling:{battle.id}", 60)

        creator_steam_id = await db.scalar(
            select(User.steam_id).
            where(User.id == battle.creator_id)
        )
        opponent_steam_id = await db.scalar(
            select(User.steam_id).
            where(User.id == battle.opponent_id)
        )

        if not creator_steam_id or not opponent_steam_id:
            logger.warning("У одного из участников баттла {id} нет Steam ID", id=battle.id)
            return

        creator_matches = await opendota_client.get_player_matches(
            steam_id=creator_steam_id,
            limit=100
        )
        opponent_matches = await opendota_client.get_player_matches(
            steam_id=opponent_steam_id,
            limit=100
        )

        opponent_correct_matches = []
        creator_correct_matches = []

        existing = await db.scalars(
            select(BattleMatchEvent.match_id).where(BattleMatchEvent.battle_id == battle.id)
        )

        existing_ids = set(existing.all())

        for match in creator_matches:
            if match.get('game_mode') in VALID_GAME_MODES:
                if match.get("start_time", 0) > battle.starts_at.timestamp():
                    if match["match_id"] not in existing_ids:
                        creator_correct_matches.append(match)

        for match in opponent_matches:
            if match.get('game_mode') in VALID_GAME_MODES:
                if match.get("start_time", 0) > battle.starts_at.timestamp():
                    if match["match_id"] not in existing_ids:
                        opponent_correct_matches.append(match)

        creator_values = []
        opponent_values = []

        for match in creator_correct_matches:
            player_won = (match["player_slot"] < 128) == match["radiant_win"]

            creator_values.append({
                "battle_id": battle.id,
                "match_id": match["match_id"],
                "account_id": creator_steam_id,
                "hero_id": match.get("hero_id", 0),
                "kills": match.get("kills", 0),
                "deaths": match.get("deaths", 0),
                "assists": match.get("assists", 0),
                "win": player_won,
            })

        for match in opponent_correct_matches:
            player_won = (match["player_slot"] < 128) == match["radiant_win"]

            opponent_values.append({
                "battle_id": battle.id,
                "match_id": match["match_id"],
                "account_id": opponent_steam_id,
                "hero_id": match.get("hero_id", 0),
                "kills": match.get("kills", 0),
                "deaths": match.get("deaths", 0),
                "assists": match.get("assists", 0),
                "win": player_won,
            })

        all_values = creator_values + opponent_values

        if all_values:
            stmt = pg_insert(BattleMatchEvent).values(all_values)
            stmt = stmt.on_conflict_do_nothing(
                constraint="uq_battle_match"
            )
            await db.execute(stmt)
            await db.commit()

        await BattleService._check_battle_winner(
            db=db,
            battle=battle,
            steam_id_creator=creator_steam_id,
            steam_id_opponent=opponent_steam_id,
        )

        battle.last_polled_at = datetime.now(UTC)
        await db.commit()

    @staticmethod
    async def check_expired(db: AsyncSession) -> None:
        """Завершает баттлы, у которых истекло время.

        - pending баттлы старше 24ч → cancelled
        - active баттлы старше 48ч от starts_at → finished (ничья, winner_id = None)
        """
        now = datetime.now(UTC)

        # Просроченные pending (ожидают принятия больше 24ч)
        expired_pending = await db.scalars(
            select(Battle).where(
                Battle.status == BattleStatus.pending.value,
                Battle.created_at < now,
            )
        )

        for battle in expired_pending.all():
            battle.status = BattleStatus.cancelled.value
            battle.finished_at = now
            logger.info("Истёк pending баттл {id}", id=battle.id)

        # Просроченные active (активны больше 48ч от starts_at)
        expired_active = await db.scalars(
            select(Battle).where(
                Battle.status == BattleStatus.active.value,
                Battle.starts_at < now,
            )
        )

        for battle in expired_active.all():
            battle.status = BattleStatus.finished.value
            battle.winner_id = None  # ничья
            battle.finished_at = now
            logger.info("Истёк active баттл {id} — ничья", id=battle.id)

        await db.commit()

    @staticmethod
    async def get_battle_by_id(db: AsyncSession, id: int) -> Battle:
        result = await db.scalar(select(Battle).where(Battle.id == id))
        if not result:
            raise BattleError(status_code=404, message='Батл не найден')
        return result

    @staticmethod
    async def _check_battle_winner(
            db: AsyncSession,
            battle: Battle,
            steam_id_creator: int,
            steam_id_opponent: int,
            wins_needed: int = WINS_TO_VICTORY,
    ) -> bool:
        """Проверяет, набрал ли кто-то N побед.
        Если да — завершает баттл. Возвращает True если завершён."""

        creator_wins = await db.scalar(
            select(func.count(BattleMatchEvent.id)).where(
                BattleMatchEvent.battle_id == battle.id,
                BattleMatchEvent.account_id == steam_id_creator,
                BattleMatchEvent.win,
            )
        )

        opponent_wins = await db.scalar(
            select(func.count(BattleMatchEvent.id)).where(
                BattleMatchEvent.battle_id == battle.id,
                BattleMatchEvent.account_id == steam_id_opponent,
                BattleMatchEvent.win,
            )
        )

        if creator_wins >= wins_needed:
            battle.status = BattleStatus.finished.value
            battle.winner_id = battle.creator_id
            battle.finished_at = datetime.now(UTC)
            logger.info(
                "Баттл {id} завершён. Победитель (creator): {wins} побед",
                id=battle.id,
                wins=creator_wins
            )
            return True

        if opponent_wins >= wins_needed:
            battle.status = BattleStatus.finished.value
            battle.winner_id = battle.opponent_id
            battle.finished_at = datetime.now(UTC)
            logger.info(
                "Баттл {id} завершён. Победитель (opponent): {wins} побед",
                id=battle.id,
                wins=opponent_wins
            )
            return True

        return False
