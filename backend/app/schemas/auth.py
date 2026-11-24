from pydantic import BaseModel


class CurrentUser(BaseModel):
    id: int
    telegram_id: int
    steam_id: int | None = None
    nickname: str | None = None
    avatar_url: str | None = None


class LinkSteamRequest(BaseModel):
    steam_id: str  # строка (может быть SteamID64), нормализуется на бэкенде
