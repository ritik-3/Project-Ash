from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Ash Assistant"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    ollama_base_url: str = "http://localhost:11434"
    gemini_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
