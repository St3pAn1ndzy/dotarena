from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BattleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creator_id: int
    opponent_id: int | None = None
    winner_id: int | None = None

    status: str
    invite_token: str

    created_at: datetime
    finished_at: datetime | None
    starts_at: datetime | None


class CreateBattleRequest(BaseModel):
    opponent_id: int | None = None


class AcceptBattleRequest(BaseModel):
    invite_token: str
