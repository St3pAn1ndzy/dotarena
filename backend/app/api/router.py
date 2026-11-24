from fastapi import APIRouter

from app.api.heroes import router as heroes_router
from app.api.profile import router as profile_router

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(profile_router)
router.include_router(heroes_router)
