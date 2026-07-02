from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env", env_prefix="APP_")
   
    api_key: str
    max_file_size_mb: int = 10
    grmini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

@lru_cache
def get_settings() -> Settings:
    return Settings()