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
        filename = f"{session_id}_{sequence}_{timestamp}.mp3"
        file_path = os.path.join(settings.AUDIO_STORAGE_DIR, filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(chunk_data)
        
        session_info = self.sessions.get(session_id, {})
        sample_rate = session_info.get("sample_rate", settings.SAMPLE_RATE)
        
        estimated_pcm_size = len(chunk_data) * 10  
        calculated_duration_ms = (estimated_pcm_size / (sample_rate * settings.CHANNELS * settings.SAMPLE_WIDTH)) * 1000
        final_duration_ms = actual_duration_ms if actual_duration_ms is not None else calculated_duration_ms
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audio_sessions (session_id, chunk_sequence, file_path, file_size, duration_ms, actual_duration_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, sequence, file_path, len(chunk_data), settings.CHUNK_DURATION_MS, final_duration_ms))
        conn.commit()
        conn.close()
        
        return file_path
    
    def convert_to_mp3(self, audio_data: bytes, sample_rate: int = settings.SAMPLE_RATE) -> bytes:
        try:
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(settings.CHANNELS)
                wav_file.setsampwidth(settings.SAMPLE_WIDTH)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data)
            
            wav_io.seek(0)
            audio_segment = AudioSegment.from_wav(wav_io)
            mp3_io = io.BytesIO()
            audio_segment.export(mp3_io, format="mp3", bitrate="64k")
            return mp3_io.getvalue()
        except Exception as e:
            print(f"Error converting to MP3: {e}")
            return b""
