import pytest_asyncio

from app.integrations.opendota import opendota_client


@pytest_asyncio.fixture(autouse=True)
async def cleanup_opendota_session():
    """Закрываем aiohttp-сессию после каждого теста."""
    yield
    if opendota_client._session is not None and not opendota_client._session.closed:
        await opendota_client._session.close()
