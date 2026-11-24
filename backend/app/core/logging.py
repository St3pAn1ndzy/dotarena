import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Настраивает loguru для всего приложения.

    - В консоль: цветной вывод, уровень DEBUG при debug=True, иначе INFO
    - В файл: ротация по дням, уровень INFO
    """
    log_level = "DEBUG" if settings.debug else "INFO"

    logger.remove()

    # Консоль — цветной вывод, удобный для разработки
    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # Файл — структурированный лог с ротацией
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "dotarena_{time:YYYY-MM-DD}.log",
        level="INFO",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        rotation="1 day",
        retention="7 days",
        compression="gz",
    )

    logger.info(
        "Логгирование настроено. Уровень: {level}, файл: {log_file}",
        level=log_level,
        log_file=str(log_dir),
    )


# Экспортируем logger для использования в других модулях
__all__ = ["logger", "setup_logging"]