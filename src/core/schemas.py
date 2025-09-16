from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChunkSchema(BaseModel):
    sequence: int
    file_path: str
    timestamp: datetime
    file_size: int
    expected_duration_ms: int
    actual_duration_ms: Optional[float]
    transcription: Optional[str]

class SessionSchema(BaseModel):
    session_id: str
    chunk_count: int
    first_chunk: datetime
    last_chunk: datetime
    total_size: int
    avg_actual_duration_ms: Optional[float]
