from fastapi import Path

from app.core.steam import normalize_steam_id


def steam_id_dependency(steam_id: int = Path(...)) -> int:
    """Нормализует Steam ID и возвращает account_id"""
    return normalize_steam_id(steam_id)
