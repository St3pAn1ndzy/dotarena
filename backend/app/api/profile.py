from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query

from app.core.cache import cache
from app.core.constants import VALID_GAME_MODES
from app.core.dependencies import steam_id_dependency
from app.core.logging import logger
from app.integrations.opendota import opendota_client
from app.schemas.match import MatchSummary
from app.schemas.profile import PlayerProfile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{steam_id}", response_model=PlayerProfile)
async def get_profile(account_id: int = Depends(steam_id_dependency)) -> PlayerProfile:
    logger.info("Запрос профиля: account_id={id}", id=account_id)

    cached = await cache.get(f"profile:{account_id}")
    if cached is not None:
        logger.debug("Профиль из кэша: account_id={id}", id=account_id)
        return PlayerProfile(**cached)

    data = await opendota_client.get_player_profile(account_id)
    if data is None:
        logger.warning("Профиль не найден: account_id={id}", id=account_id)
        raise HTTPException(status_code=404, detail="Player not found")

    profile_data = data.get("profile", {})

    result = PlayerProfile(
        steam_id=profile_data["account_id"],
        nickname=profile_data.get("personaname"),
        avatar=profile_data.get("avatarfull"),
        leaderboard_rank=data.get("leaderboard_rank"),
    )

    await cache.set(f"profile:{account_id}", result.model_dump(), ttl=300)
    logger.debug("Профиль сохранён в кэш: account_id={id}", id=account_id)

    return result


@router.get("/{steam_id}/matches")
async def get_profile_matches(
    account_id: int = Depends(steam_id_dependency),
    limit: Annotated[int, Query(gt=0)] = 20,
) -> list[MatchSummary]:
    logger.info("Запрос матчей: account_id={id}, limit={limit}", id=account_id, limit=limit)

    cached = await cache.get(f"matches:{account_id}:{limit}")
    if cached is not None:
        logger.debug("Матчи из кэша: account_id={id}", id=account_id)
        return [MatchSummary(**m) for m in cached]

    data = await opendota_client.get_player_matches(account_id, limit)
    if not data:
        logger.info("Матчи не найдены: account_id={id}", id=account_id)
        return []

    # фильтрация game_mode
    filtered = [m for m in data if m.get("game_mode") in VALID_GAME_MODES]
    logger.debug(
        "Отфильтровано матчей: {total} → {filtered} (game_mode in {modes})",
        total=len(data),
        filtered=len(filtered),
        modes=VALID_GAME_MODES,
    )

    result = [MatchSummary(
        match_id=m["match_id"],
        hero_id=m.get("hero_id", 0),
        kills=m.get("kills", 0),
        deaths=m.get("deaths", 0),
        assists=m.get("assists", 0),
        radiant_win=m.get("radiant_win", False),
        player_slot=m.get("player_slot"),
        game_mode=m.get("game_mode", 0),
        duration=m.get("duration", 0),
        start_time=m.get("start_time", 0),
    ) for m in filtered]

    await cache.set(f"matches:{account_id}:{limit}", [r.model_dump() for r in result], ttl=300)
    logger.debug("Матчи сохранены в кэш: account_id={id}, count={count}", id=account_id, count=len(result))

    return result
