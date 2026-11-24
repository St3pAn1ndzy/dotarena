from fastapi import APIRouter

from app.api.profile import router as profile_router

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(profile_router)


@router.get("/health")
def health():
    return {"status": "ok"}
