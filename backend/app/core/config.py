from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dotarena"
    redis_url: str = "redis://localhost:6379/0"
    public_url: str = "http://localhost:5173"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()  # type: ignore[call-arg]
