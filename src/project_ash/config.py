from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    enable_tts: bool = False
    log_dir: Path = Path(".project_ash")
    sqlite_db_path: Path = Path(".project_ash/ash_memory.db")
    ollama_model: str = "llama3.1:8b-instruct-q4_K_M"
    faster_whisper_model: str = "small"
    faster_whisper_device: str = "cuda"
    piper_model_path: str | None = None
    piper_exe: str = "piper"
    playwright_user_data_dir: Path = Path(".project_ash/playwright-profile")
    playwright_headless: bool = False
    playwright_timeout_ms: int = 15000
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    channel_providers_enabled: list[str] = None  # type: ignore[assignment]
    enable_injection_guard: bool = True
    redact_logs: bool = True

    def __post_init__(self) -> None:
        if self.channel_providers_enabled is None:
            object.__setattr__(self, "channel_providers_enabled", ["telegram", "slack", "discord", "whatsapp"])


def _merge_json_config(defaults: AppConfig, config_data: dict[str, Any]) -> AppConfig:
    merged = {
        "enable_tts": bool(config_data.get("enable_tts", defaults.enable_tts)),
        "log_dir": Path(config_data.get("log_dir", defaults.log_dir)),
        "sqlite_db_path": Path(config_data.get("sqlite_db_path", defaults.sqlite_db_path)),
        "ollama_model": str(config_data.get("ollama_model", defaults.ollama_model)),
        "faster_whisper_model": str(config_data.get("faster_whisper_model", defaults.faster_whisper_model)),
        "faster_whisper_device": str(config_data.get("faster_whisper_device", defaults.faster_whisper_device)),
        "piper_model_path": config_data.get("piper_model_path", defaults.piper_model_path),
        "piper_exe": str(config_data.get("piper_exe", defaults.piper_exe)),
        "playwright_user_data_dir": Path(
            config_data.get("playwright_user_data_dir", defaults.playwright_user_data_dir)
        ),
        "playwright_headless": bool(config_data.get("playwright_headless", defaults.playwright_headless)),
        "playwright_timeout_ms": int(config_data.get("playwright_timeout_ms", defaults.playwright_timeout_ms)),
        "api_host": str(config_data.get("api_host", defaults.api_host)),
        "api_port": int(config_data.get("api_port", defaults.api_port)),
        "channel_providers_enabled": list(
            config_data.get("channel_providers_enabled", defaults.channel_providers_enabled)
        ),
        "enable_injection_guard": bool(config_data.get("enable_injection_guard", defaults.enable_injection_guard)),
        "redact_logs": bool(config_data.get("redact_logs", defaults.redact_logs)),
    }
    return AppConfig(**merged)


def load_default_config() -> AppConfig:
    defaults = AppConfig()
    config_path = Path("configs/app_config.json")

    if not config_path.exists():
        return defaults

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return defaults
        return _merge_json_config(defaults, raw)
    except (OSError, ValueError, TypeError):
        return defaults
