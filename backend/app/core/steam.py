STEAMID64_OFFSET = 76561197960265728


def normalize_steam_id(steam_id: int) -> int:
    """Приводит SteamID64 (17 цифр) к 32-битному account_id."""
    if steam_id > STEAMID64_OFFSET:
        return steam_id - STEAMID64_OFFSET
    return steam_id
