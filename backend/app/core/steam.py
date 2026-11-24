from app.core.logging import logger

STEAMID64_OFFSET = 76561197960265728


def normalize_steam_id(steam_id: int) -> int:
    """Приводит SteamID64 (17 цифр) к 32-битному account_id."""
    if steam_id > STEAMID64_OFFSET:
        account_id = steam_id - STEAMID64_OFFSET
        logger.debug("SteamID64 → account_id: {steam} → {acc}", steam=steam_id, acc=account_id)
        return account_id
    return steam_id
