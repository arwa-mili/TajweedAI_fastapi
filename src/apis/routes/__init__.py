from fastapi import APIRouter
from . import sessions, health

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
