from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.tasks.poll_battle import poll_active_battles, check_expired_battles

engine = create_async_engine(settings.database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def startup(ctx: dict) -> None:
    ctx["session_factory"] = session_factory
    ctx["db"] = session_factory()


async def shutdown(ctx: dict) -> None:
    db: AsyncSession = ctx["db"]
    await db.close()
    await engine.dispose()


class WorkerSettings:
    functions = [poll_active_battles, check_expired_battles]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    keep_result = 0  # не хранить результаты задач
    poll_delay = 0.5  # частота опроса очереди
    cron_jobs = [
        # запускать poll_active_battles каждые 45 минут
        {"func": poll_active_battles, "cron": "0 */45 * * *", "timeout": 300},
        # запускать check_expired_battles раз в час
        {"func": check_expired_battles, "cron": "0 0 * * *", "timeout": 60},
    ]
