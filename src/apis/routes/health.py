from fastapi import APIRouter
from datetime import datetime
from src.core.config import settings

router = APIRouter()

@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "storage_dir": settings.AUDIO_STORAGE_DIR,
        "database": settings.DB_PATH,
        "expected_chunk_duration_ms": settings.CHUNK_DURATION_MS
    }
