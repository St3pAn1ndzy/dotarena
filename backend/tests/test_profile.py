from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

# ID, на который OpenDota точно не имеет данных
UNKNOWN_ID = 2147483647


async def test_health_endpoint():
    """GET /health возвращает 200"""
    from app.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@patch("app.api.profile.cache.get", new_callable=AsyncMock, return_value=None)
@patch("app.api.profile.cache.set", new_callable=AsyncMock)
async def test_profile_not_found(mock_set, mock_get):
    """Несуществующий игрок — 404"""
    from app.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/api/profile/{UNKNOWN_ID}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Player not found"


@patch("app.api.profile.cache.get", new_callable=AsyncMock, return_value=None)
@patch("app.api.profile.cache.set", new_callable=AsyncMock)
async def test_profile_dendi(mock_set, mock_get):
    """Профиль Dendi возвращается с корректными полями"""
    from app.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/profile/70388657")
    assert resp.status_code == 200
    data = resp.json()
    assert data["steam_id"] == 70388657
    assert data["nickname"] is not None
    assert data["avatar"] is not None
    assert data["avatar"].startswith("http")


@patch("app.api.profile.cache.get", new_callable=AsyncMock, return_value=None)
@patch("app.api.profile.cache.set", new_callable=AsyncMock)
async def test_profile_matches(mock_set, mock_get):
    """Матчи возвращаются с корректными полями"""
    from app.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/profile/70388657/matches?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    for match in data:
        assert "match_id" in match
        assert "hero_id" in match
        assert "player_slot" in match
        assert "game_mode" in match
        assert match["game_mode"] in (1, 22)


@patch("app.api.heroes.cache.get", new_callable=AsyncMock, return_value=None)
@patch("app.api.heroes.cache.set", new_callable=AsyncMock)
async def test_profile_heroes(mock_set, mock_get):
    """Статистика по героям возвращается"""
    from app.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/profile/70388657/heroes")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@patch("app.api.profile.cache.get", new_callable=AsyncMock, return_value=None)
@patch("app.api.profile.cache.set", new_callable=AsyncMock)
async def test_profile_with_steamid64(mock_set, mock_get):
    """SteamID64 нормализуется в account_id"""
    from app.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/profile/76561198030654385")
    assert resp.status_code == 200
    assert resp.json()["steam_id"] == 70388657
