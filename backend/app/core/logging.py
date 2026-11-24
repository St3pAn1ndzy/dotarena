import sys
from contextvars import ContextVar
from pathlib import Path

from loguru import logger

from app.core.config import settings

# Хранит request_id для текущего запроса (контекстная переменная)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return request_id_var.get(None)


def set_request_id(request_id: str) -> None:
    request_id_var.set(request_id)


def setup_logging() -> None:
    """Настраивает loguru для всего приложения.

    - В консоль: цветной вывод, уровень DEBUG при debug=True, иначе INFO
    - В файл: ротация по дням, уровень INFO
    """
    log_level = "DEBUG" if settings.debug else "INFO"

    logger.remove()

    # Кастомный формат с request_id
    log_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[request_id]: >12}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Консоль — цветной вывод
    logger.add(
        sys.stdout,
        level=log_level,
        format=log_format,
        colorize=True,
        filter=_inject_request_id,
    )

    # Файл — структурированный лог с ротацией
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{extra[request_id]: >12} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    logger.add(
        log_dir / "dotarena_{time:YYYY-MM-DD}.log",
        level="INFO",
        format=file_format,
        rotation="1 day",
        retention="7 days",
        compression="gz",
        filter=_inject_request_id,
    )

    logger.info(
        "Логгирование настроено. Уровень: {level}, файл: {log_file}",
        level=log_level,
        log_file=str(log_dir),
    )


def _inject_request_id(record) -> bool:
    """Добавляет request_id в extra каждого лог-сообщения."""
    rid = get_request_id()
    record["extra"]["request_id"] = rid or "-"
    return True


# Экспортируем logger для использования в других модулях
__all__ = ["logger", "setup_logging", "set_request_id", "get_request_id"]