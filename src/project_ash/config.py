from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    enable_tts: bool = False
    log_dir: Path = Path(".project_ash")
    sqlite_db_path: Path = Path(".project_ash/ash_memory.db")
    ollama_model: str = "llama3.1:8b-instruct-q4_K_M"
    faster_whisper_model: str = "small"
    faster_whisper_device: str = "cuda"
    piper_model_path: str | None = None
    api_host: str = "127.0.0.1"
    api_port: int = 8000


def load_default_config() -> AppConfig:
    return AppConfig()
