from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.steam import normalize_steam_id
from app.models.user import User
from app.schemas.auth import CurrentUser, LinkSteamRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUser)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.put("/steam", response_model=CurrentUser)
async def link_steam(
    body: LinkSteamRequest,
    current_user: User = Depends(get_current_user),
) -> User:
    account_id = normalize_steam_id(int(body.steam_id))
    current_user.steam_id = account_id
    return current_user