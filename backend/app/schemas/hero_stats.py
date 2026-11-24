from pydantic import BaseModel


class HeroStats(BaseModel):
    hero_id: int
    games: int
    win: int
    kills: float
    deaths: float
    assists: float
    last_played: int
