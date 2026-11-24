from fastapi import APIRouter, HTTPException

from app.core.cache import cache
from app.integrations.opendota import opendota_client
from app.schemas.profile import PlayerProfile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/{steam_id}", response_model=PlayerProfile)
async def get_profile(steam_id: int) -> PlayerProfile:

    cached = await cache.get(f"profile:{steam_id}")
    if cached is not None:
        return PlayerProfile(**cached)

    data = await opendota_client.get_player_profile(steam_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Player not found")

    profile_data = data.get("profile", {})

    result = PlayerProfile(
        steam_id=profile_data["account_id"],
        nickname=profile_data.get("personaname"),
        avatar=profile_data.get("avatarfull"),
        rank_tier=data.get("rank_tier"),
        leaderboard_rank=data.get("leaderboard_rank"),
        mmr=data.get("computed_mmr"),
    )

    await cache.set(f"profile:{steam_id}", result.model_dump(), ttl=300)

    return result
