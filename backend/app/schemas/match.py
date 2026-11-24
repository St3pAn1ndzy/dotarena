from pydantic import BaseModel


class MatchSummary(BaseModel):
    match_id: int
    hero_id: int
    kills: int
    deaths: int
    assists: int
    radiant_win: bool
    player_slot: int
    game_mode: int
    duration: int  # в секундах
    start_time: int  # unix timestamp
