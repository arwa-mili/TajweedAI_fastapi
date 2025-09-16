import os
import io
from datetime import datetime
from pydub import AudioSegment
from src.core.config import settings
from src.db.repositories import insert_audio_chunk


class AudioService:
    def __init__(self):
        self.sessions = {}
        self.timings = {}
        self.buffers = {}

    def _normalize_format(self, mime_or_format: str | None) -> str:
        if not mime_or_format:
            return "wav"
        value = str(mime_or_format).lower()
        # Extract before ';' if MIME
        if ";" in value:
            value = value.split(";", 1)[0]
        # Extract after '/' if MIME
        if "/" in value:
            value = value.split("/", 1)[1]
        # Common aliases
        if value in ("x-wav", "wave"):
            return "wav"
        if value in ("x-ogg",):
            return "ogg"
        if value.startswith("webm"):
            return "webm"
        if value.startswith("ogg"):
            return "ogg"
        if value.startswith("wav"):
            return "wav"
        if value.startswith("mp3"):
            return "mp3"
        if value.startswith("m4a") or value.startswith("mp4") or value.startswith("aac"):
            return "m4a"
        return value

    async def save_chunk(
        self,
        session_id: str,
        chunk_data: bytes,
        sequence: int,
        actual_duration_ms: float = None,
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{session_id}_{sequence}_{timestamp}.wav"
        path = os.path.join(settings.AUDIO_STORAGE_DIR, filename)
        os.makedirs(settings.AUDIO_STORAGE_DIR, exist_ok=True)

        session = self.sessions.get(session_id, {})
        audio_format = self._normalize_format(session.get("format") or session.get("mime"))

        buffer = self.buffers.setdefault(session_id, bytearray())

        def try_decode(data: bytes):
            try:
                return AudioSegment.from_file(io.BytesIO(data), format=audio_format)
            except Exception:
                return AudioSegment.from_file(io.BytesIO(data))

        try:
            audio_segment = try_decode(chunk_data)
        except Exception as e:
            buffer.extend(chunk_data)
            try:
                audio_segment = try_decode(bytes(buffer))
            except Exception:
                # Keep buffering until a decodable container is available, but cap size
                max_buffer_bytes = 5 * 1024 * 1024
                if len(buffer) > max_buffer_bytes:
                    # Reset corrupted buffer to avoid unbounded growth
                    self.buffers[session_id] = bytearray()
                    print("Failed to decode audio chunk: buffer reset due to size cap", e)
                else:
                    print("Partial/undecodable chunk buffered, waiting for more bytes")
                return None

        # Reset buffer
        self.buffers[session_id] = bytearray()
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        audio_segment.export(path, format="wav")

        # Save
        await insert_audio_chunk(
            session_id=session_id,
            sequence=sequence,
            file_path=path,
            size=len(chunk_data),
            duration_ms=settings.CHUNK_DURATION_MS,
            actual_duration_ms=actual_duration_ms,
            sura=session.get("sura_number"),
            ayat_begin=session.get("ayat_begin"),
            ayat_end=session.get("ayat_end"),
            word_begin=session.get("word_begin"),
            word_end=session.get("word_end"),
        )
        print(f"Saved chunk {sequence}, size {len(chunk_data)} bytes")
        return path
