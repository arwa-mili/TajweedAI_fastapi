from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SAMPLE_RATE : int
    CHANNELS : int
    SAMPLE_WIDTH : int
    CHUNK_DURATION_MS : int  
    DB_PATH : str
    AUDIO_STORAGE_DIR : str
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()