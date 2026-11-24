from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUser)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
