from fastapi import APIRouter, Depends, HTTPException

from app.core.cache import cache
from app.core.dependencies import steam_id_dependency
from app.core.logging import logger
from app.integrations.opendota import opendota_client
from app.schemas.hero_stats import HeroStats

router = APIRouter(prefix="/profile", tags=["heroes"])


@router.get("/{steam_id}/heroes")
async def get_player_heroes(account_id: int = Depends(steam_id_dependency)) -> list[HeroStats]:
    logger.info("Запрос статистики по героям: account_id={id}", id=account_id)

    cached = await cache.get(f"heroes:{account_id}")
    if cached is not None:
        logger.debug("Герои из кэша: account_id={id}", id=account_id)
        return [HeroStats(**h) for h in cached]

    data = await opendota_client.get_player_heroes(account_id)
    if data is None:
        logger.warning("Статистика по героям не найдена: account_id={id}", id=account_id)
        raise HTTPException(status_code=404, detail="Heroes not found")

    # Сортируем по games (убывание) и берём топ-10
    sorted_data = sorted(data, key=lambda h: h.get("games", 0), reverse=True)
    top = [HeroStats(
        hero_id=h["hero_id"],
        games=h["games"],
        win=h["win"],
        kills=h.get("kills", 0.0),
        deaths=h.get("deaths", 0.0),
        assists=h.get("assists", 0.0),
        last_played=h.get("last_played", 0),
    ) for h in sorted_data[:10]]

    await cache.set(f"heroes:{account_id}", [h.model_dump() for h in top], ttl=600)
    logger.debug("Герои сохранены в кэш: account_id={id}, count={count}", id=account_id, count=len(top))

    return top