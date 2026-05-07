from dataclasses import dataclass
from functools import lru_cache
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    """Load optional .env files for first-time local runs."""
    here = Path(__file__).resolve()
    service_root = here.parents[2]
    repo_root = here.parents[4]

    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(service_root / ".env", override=True)


_load_env()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def _as_float(value: str | None, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def _path_or_none(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value)


@dataclass(slots=True)
class Settings:
    app_name: str
    app_version: str
    api_v1_prefix: str
    ollama_base_url: str
    ollama_model: str
    wake_word_model_name: str
    wake_word_threshold: float
    wake_word_timeout_seconds: float
    audio_sample_rate: int
    audio_channels: int
    audio_input_device: int | None
    audio_output_device: int | None
    utterance_record_seconds: float
    utterance_min_record_seconds: float
    utterance_silence_seconds: float
    utterance_silence_threshold: float
    utterance_chunk_seconds: float
    stt_model: str
    stt_device: str
    stt_compute_type: str
    stt_min_transcript_chars: int
    stt_min_avg_logprob: float
    stt_max_no_speech_prob: float
    tts_voice_model_path: Path | None
    tts_voice_config_path: Path | None
    tts_use_cuda: bool
    session_memory_limit: int
    conversation_temperature: float
    conversation_language: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=getenv("APP_NAME", "Ash Assistant"),
            app_version=getenv("APP_VERSION", "0.1.0"),
            api_v1_prefix=getenv("API_V1_PREFIX", "/api/v1"),
            ollama_base_url=getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
            ollama_model=getenv("OLLAMA_MODEL", "llama3.1:8b-instruct"),
            wake_word_model_name=getenv("WAKE_WORD_MODEL", "hey_jarvis"),
            wake_word_threshold=_as_float(getenv("WAKE_WORD_THRESHOLD"), 0.6),
            wake_word_timeout_seconds=_as_float(getenv("WAKE_WORD_TIMEOUT_SECONDS"), 20.0),
            audio_sample_rate=_as_int(getenv("AUDIO_SAMPLE_RATE"), 16000),
            audio_channels=_as_int(getenv("AUDIO_CHANNELS"), 1),
            audio_input_device=_as_int(getenv("AUDIO_INPUT_DEVICE"), 0) if getenv("AUDIO_INPUT_DEVICE") else None,
            audio_output_device=_as_int(getenv("AUDIO_OUTPUT_DEVICE"), 0) if getenv("AUDIO_OUTPUT_DEVICE") else None,
            utterance_record_seconds=_as_float(getenv("UTTERANCE_RECORD_SECONDS"), 6.0),
            utterance_min_record_seconds=_as_float(getenv("UTTERANCE_MIN_RECORD_SECONDS"), 0.8),
            utterance_silence_seconds=_as_float(getenv("UTTERANCE_SILENCE_SECONDS"), 0.7),
            utterance_silence_threshold=_as_float(getenv("UTTERANCE_SILENCE_THRESHOLD"), 0.012),
            utterance_chunk_seconds=_as_float(getenv("UTTERANCE_CHUNK_SECONDS"), 0.12),
            stt_model=getenv("VOICE_STT_MODEL", "small"),
            stt_device=getenv("STT_DEVICE", "auto"),
            stt_compute_type=getenv("STT_COMPUTE_TYPE", "int8"),
            stt_min_transcript_chars=_as_int(getenv("STT_MIN_TRANSCRIPT_CHARS"), 5),
            stt_min_avg_logprob=_as_float(getenv("STT_MIN_AVG_LOGPROB"), -1.0),
            stt_max_no_speech_prob=_as_float(getenv("STT_MAX_NO_SPEECH_PROB"), 0.55),
            tts_voice_model_path=_path_or_none(getenv("PIPER_VOICE_MODEL_PATH")),
            tts_voice_config_path=_path_or_none(getenv("PIPER_VOICE_CONFIG_PATH")),
            tts_use_cuda=_as_bool(getenv("PIPER_USE_CUDA"), False),
            session_memory_limit=_as_int(getenv("SESSION_MEMORY_LIMIT"), 8),
            conversation_temperature=_as_float(getenv("CONVERSATION_TEMPERATURE"), 0.7),
            conversation_language=getenv("CONVERSATION_LANGUAGE", "en"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
