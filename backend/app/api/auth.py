from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.logging import logger
from app.core.steam import normalize_steam_id
from app.models.user import User
from app.schemas.auth import CurrentUser, LinkSteamRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUser)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user),
) -> User:
    logger.info("Текущий пользователь: telegram_id={id}, steam_id={steam}",
                id=current_user.telegram_id, steam=current_user.steam_id)
    return current_user


@router.put("/steam", response_model=CurrentUser)
async def link_steam(
    body: LinkSteamRequest,
    current_user: User = Depends(get_current_user),
) -> User:
    account_id = normalize_steam_id(int(body.steam_id))
    current_user.steam_id = account_id
    logger.info("Steam ID привязан: telegram_id={tg}, steam_id={steam}",
                tg=current_user.telegram_id, steam=account_id)
    return current_user