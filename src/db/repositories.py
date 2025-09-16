from src.db.database import get_connection


async def insert_audio_chunk(**kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audio_sessions (
            session_id, chunk_sequence, file_path, file_size, 
            duration_ms, actual_duration_ms, sura_number, 
            ayat_begin, ayat_end, word_begin, word_end
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        kwargs["session_id"], kwargs["sequence"], kwargs["file_path"], kwargs["size"],
        kwargs["duration_ms"], kwargs["actual_duration_ms"], kwargs["sura"],
        kwargs["ayat_begin"], kwargs["ayat_end"], kwargs["word_begin"], kwargs["word_end"]
    ))
    conn.commit()
    conn.close()
