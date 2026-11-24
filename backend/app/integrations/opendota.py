import asyncio
import time
from typing import Any

import aiohttp

from app.core.config import settings


class OpenDotaClient:
    BASE_URL = settings.open_dota_url

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._last_request_time: float = 0.0

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(self, path: str) -> Any | None:
        """Общий метод для всех запросов к OpenDota"""
        # Rate limiting: не чаще 1 запроса в секунду (60/мин)
        now = time.monotonic()
        since_last = now - self._last_request_time
        if since_last < 1.0:
            await asyncio.sleep(1.0 - since_last)

        session = await self._ensure_session()
        url = f"{self.BASE_URL}{path}"

        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                self._last_request_time = time.monotonic()

                if resp.status == 404:
                    return None
                if resp.status == 429:
                    # Слишком много запросов — подождать и повторить
                    await asyncio.sleep(5)
                    return await self._request(path)
                resp.raise_for_status()
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"[OpenDota] Request failed: {e}")
            return None

    async def get_player_profile(self, steam_id: int) -> dict | None:
        """Возвращает профиль игрока или None если 404"""
        result = await self._request(f"/players/{steam_id}")
        return result if isinstance(result, dict) else None

    async def get_player_matches(
        self,
        steam_id: int,
        limit: int = 20,
    ) -> list[dict]:
        """Возвращает список последних матчей с полной информацией об игроках"""
        result = await self._request(
            f"/players/{steam_id}/matches?project=players&limit={limit}",
        )
        return result if isinstance(result, list) else []


# Единственный экземпляр на всё приложение
opendota_client = OpenDotaClient()
