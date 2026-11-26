from fastapi import APIRouter, HTTPException

from app.core.dependencies import CurrentUserDep, SessionDep
from app.models import Battle
from app.schemas.battle import BattleResponse
from app.services.battle import BattleService

router = APIRouter(prefix="/battles", tags=["battles"])


@router.post("/", response_model=BattleResponse)
async def create_battle(
        db: SessionDep,
        current_user: CurrentUserDep
) -> Battle:
    if current_user.steam_id is None:
        raise HTTPException(status_code=400, detail="Steam ID не привязан!")

    battle = await BattleService.create_battle(db=db, creator_user=current_user)

    return battle


@router.post("/{b_id}/accept", response_model=BattleResponse)
async def accept_battle(
        b_id: int,
        db: SessionDep,
        current_user: CurrentUserDep
) -> Battle:
    if current_user.steam_id is None:
        raise HTTPException(status_code=400, detail="Steam ID не привязан!")

    battle = await BattleService.get_battle_by_id(db=db, id=b_id)

    result = await BattleService.accept_battle(db=db, battle=battle, user=current_user)
    return result


@router.post("/{b_id}/decline", response_model=BattleResponse)
async def decline_battle(
        b_id: int,
        db: SessionDep,
        current_user: CurrentUserDep
) -> Battle:
    if current_user.steam_id is None:
        raise HTTPException(status_code=400, detail="Steam ID не привязан!")

    battle = await BattleService.get_battle_by_id(db=db, id=b_id)

    result = await BattleService.decline_battle(db=db, battle=battle, user=current_user)
    return result


@router.get("/", response_model=list[BattleResponse])
async def get_user_battles(
        db: SessionDep,
        current_user: CurrentUserDep
) -> list[Battle]:
    result = await BattleService.get_user_battles(db=db, user=current_user)
    return result


@router.get("/{b_id}", response_model=BattleResponse)
async def get_battle(
        b_id: int,
        db: SessionDep,
        current_user: CurrentUserDep
) -> Battle:
    battle = await BattleService.get_battle_by_id(db=db, id=b_id)
    return battle
