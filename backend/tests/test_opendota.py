import pytest


@pytest.mark.asyncio
async def test_get_player_profile_found():
    """Профиль найден — возвращается словарь"""
    from app.integrations.opendota import opendota_client
    result = await opendota_client.get_player_profile(70388657)
    assert result is not None
    assert isinstance(result, dict)
    assert "profile" in result
    assert result["profile"]["account_id"] == 70388657


@pytest.mark.asyncio
async def test_get_player_profile_not_found():
    """Несуществующий игрок — возвращается None"""
    from app.integrations.opendota import opendota_client
    result = await opendota_client.get_player_profile(2147483647)
    assert result is None


@pytest.mark.asyncio
async def test_get_player_matches():
    """Матчи возвращаются как список"""
    from app.integrations.opendota import opendota_client
    result = await opendota_client.get_player_matches(70388657, limit=3)
    assert isinstance(result, list)
    assert len(result) <= 3
    if result:
        assert "match_id" in result[0]
        assert "hero_id" in result[0]
        assert "player_slot" in result[0]


@pytest.mark.asyncio
async def test_get_player_heroes():
    """Статистика по героям возвращается как список"""
    from app.integrations.opendota import opendota_client
    result = await opendota_client.get_player_heroes(70388657)
    assert isinstance(result, list)
    if result:
        assert "hero_id" in result[0]
        assert "games" in result[0]
        assert "win" in result[0]


@pytest.mark.asyncio
async def test_get_player_matches_empty():
    """У несуществующего игрока — пустой список"""
    from app.integrations.opendota import opendota_client
    result = await opendota_client.get_player_matches(2147483647)
    assert isinstance(result, list)