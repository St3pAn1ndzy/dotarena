from pydantic import BaseModel


class PlayerProfile(BaseModel):
    steam_id: int
    nickname: str | None = None
    avatar: str | None = None
    leaderboard_rank: int | None = None
