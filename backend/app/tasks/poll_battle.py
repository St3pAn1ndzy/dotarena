from sqlalchemy import select

from app.core.enums import BattleStatus
from app.core.logging import logger
from app.models.battle import Battle
from app.services.battle import BattleService


async def poll_active_battles(ctx: dict) -> None:
    """Поллит все активные баттлы. Запускается по крону каждые 45 мин."""
    db = ctx["db"]
    redis = ctx["redis"]

    active_battles = await db.scalars(
        select(Battle).where(Battle.status == BattleStatus.active.value)
    )

    for battle in active_battles.all():
        logger.info("Фоновый поллинг баттла {id}", id=battle.id)
        await BattleService.poll_battle(db=db, redis=redis, battle=battle)

    logger.info("Фоновый поллинг завершён: {count} баттлов", count=len(active_battles.all()))


async def check_expired_battles(ctx: dict) -> None:
    """Завершает просроченные баттлы. Запускается раз в час."""
    db = ctx["db"]
    await BattleService.check_expired(db=db)
    logger.info("Проверка просроченных баттлов завершена")
