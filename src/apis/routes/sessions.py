from fastapi import APIRouter
from src.db.database import get_connection

router = APIRouter()

@router.get("")
async def get_sessions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, COUNT(*) as chunk_count, 
            MIN(timestamp), MAX(timestamp),
            SUM(file_size), AVG(actual_duration_ms)
        FROM audio_sessions 
        GROUP BY session_id 
        ORDER BY MIN(timestamp) DESC
    ''')
    sessions = cursor.fetchall()
    conn.close()
    
    return {
        "sessions": [
            {
                "session_id": row[0],
                "chunk_count": row[1],
                "first_chunk": row[2],
                "last_chunk": row[3],
                "total_size": row[4],
                "avg_actual_duration_ms": row[5]
            }
            for row in sessions
        ]
    }

@router.get("/{session_id}")
async def get_session_details(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT chunk_sequence, file_path, timestamp, file_size, duration_ms, actual_duration_ms
        FROM audio_sessions 
        WHERE session_id = ?
        ORDER BY chunk_sequence
    ''', (session_id,))
    chunks = cursor.fetchall()
    conn.close()
    
    if not chunks:
        return {"error": "Session not found"}
    
    return {
        "session_id": session_id,
        "chunks": [
            {
                "sequence": row[0],
                "file_path": row[1],
                "timestamp": row[2],
                "file_size": row[3],
                "expected_duration_ms": row[4],
                "actual_duration_ms": row[5]
            }
            for row in chunks
        ]
    }
