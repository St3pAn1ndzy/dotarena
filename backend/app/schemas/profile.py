from pydantic import BaseModel


class PlayerProfile(BaseModel):
    steam_id: int
    nickname: str | None = None
    avatar: str | None = None
    leaderboard_rank: int | None = None


class PlayerStats(BaseModel):
    total_games: int
    wins: int
    losses: int
    winrate: float
    avg_kills: float
    avg_deaths: float
    avg_assists: float
