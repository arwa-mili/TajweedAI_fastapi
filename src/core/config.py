from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    SAMPLE_WIDTH: int = 2
    CHUNK_DURATION_MS: int = 3000
    DB_PATH: str = os.path.abspath("./audio_sessions.db")
    AUDIO_STORAGE_DIR: str = os.path.abspath("./audio_chunks")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
