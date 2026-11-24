from fastapi import Depends, Header, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.core.steam import normalize_steam_id
from app.core.telegram import validate_init_data
from app.models.user import User


def steam_id_dependency(steam_id: int = Path(...)) -> int:
    """Нормализует Steam ID и возвращает account_id"""
    return normalize_steam_id(steam_id)


async def get_current_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Проверяет initData Telegram и возвращает/создаёт пользователя."""
    if not authorization:
        logger.warning("Запрос без Authorization заголовка")
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    data = validate_init_data(authorization, settings.bot_token)
    if data is None:
        logger.warning("Невалидная подпись initData")
        raise HTTPException(status_code=401, detail="Invalid init data signature")

    telegram_id = int(data.get("id", 0))
    if not telegram_id:
        logger.warning("Нет id в initData")
        raise HTTPException(status_code=401, detail="Missing user id in init data")

    # Ищем пользователя
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is not None:
        logger.debug("Найден пользователь: telegram_id={id}", id=telegram_id)
        return user

    # Создаём нового
    user = User(
        telegram_id=telegram_id,
        nickname=data.get("first_name") or data.get("username"),
        avatar_url=data.get("photo_url"),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    logger.info("Создан новый пользователь: telegram_id={id}, nickname={nick}",
                id=telegram_id, nick=user.nickname)
    return user