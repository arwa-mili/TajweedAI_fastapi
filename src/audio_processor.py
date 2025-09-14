import io
import os
import sqlite3
import wave
from datetime import datetime
from pydub import AudioSegment
import aiofiles
from .config import settings
from .database import get_connection


class AudioProcessor:
    def __init__(self):
        self.sessions = {}
        self.session_timings = {}
    
    async def save_audio_chunk(self, session_id: str, chunk_data: bytes, sequence: int, actual_duration_ms: float = None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session_info = self.sessions.get(session_id, {})
        sura_number = session_info.get("sura_number")
        ayat_begin = session_info.get("ayat_begin")
        ayat_end = session_info.get("ayat_end")
        word_begin = session_info.get("word_begin")
        word_end = session_info.get("word_end")

        
        # Create filename
        filename = f"{session_id}_{sequence}_{timestamp}.wav"
        file_path = os.path.join(settings.AUDIO_STORAGE_DIR, filename)
        
        # Wrap raw PCM bytes into proper WAV
        sample_rate = session_info.get("sample_rate", settings.SAMPLE_RATE)
        channels = session_info.get("channels", settings.CHANNELS)
        bytes_per_sample = 2  # assuming 16-bit PCM

        total_samples = len(chunk_data) // (channels * bytes_per_sample)
        calculated_duration_ms = (total_samples / sample_rate) * 1000
        final_duration_ms = actual_duration_ms if actual_duration_ms is not None else calculated_duration_ms

        # Write WAV file properly
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(bytes_per_sample)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(chunk_data)
        
        # Insert into database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audio_sessions (
                session_id, chunk_sequence, file_path, file_size, 
                duration_ms, actual_duration_ms, sura_number, 
                ayat_begin, ayat_end, word_begin,word_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, sequence, file_path, len(chunk_data), 
            settings.CHUNK_DURATION_MS, final_duration_ms, 
            sura_number, ayat_begin, ayat_end, word_begin, word_end
        ))
        conn.commit()
        conn.close()
        
        return file_path
