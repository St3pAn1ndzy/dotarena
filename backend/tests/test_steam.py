from app.core.steam import normalize_steam_id


def test_normalize_steam_id_short():
    """Короткий ID (уже account_id) не меняется"""
    assert normalize_steam_id(10482001) == 10482001
    assert normalize_steam_id(70388657) == 70388657
    assert normalize_steam_id(1) == 1


def test_normalize_steam_id_64():
    """SteamID64 нормализуется в account_id"""
    assert normalize_steam_id(76561199012147729) == 1051882001
    assert normalize_steam_id(76561198030654385) == 70388657


def test_normalize_steam_id_zero():
    """0 остаётся 0"""
    assert normalize_steam_id(0) == 0


def test_normalize_steam_id_negative():
    """Отрицательные не меняются (для безопасности)"""
    assert normalize_steam_id(-1) == -1
