from functools import lru_cache

from app.core.config import Settings, get_settings
from app.providers.llm.ollama_provider import OllamaProvider
from app.providers.stt.faster_whisper_provider import FasterWhisperTranscriber
from app.providers.tts.piper_provider import PiperTTSProvider
from app.providers.vad.silero_provider import SileroVadService
from app.providers.wakeword.openwakeword_provider import OpenWakeWordDetector
from app.services.audio_service import AudioService
from app.services.conversation_service import ConversationService
from app.services.memory_service import SessionMemoryService
from app.services.voice_session_service import VoiceSessionService


@lru_cache(maxsize=1)
def get_cached_settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_memory_service() -> SessionMemoryService:
    settings = get_cached_settings()
    return SessionMemoryService(limit=settings.session_memory_limit)


@lru_cache(maxsize=1)
def get_llm_provider() -> OllamaProvider:
    settings = get_cached_settings()
    return OllamaProvider(base_url=settings.ollama_base_url, model=settings.ollama_model)


@lru_cache(maxsize=1)
def get_conversation_service() -> ConversationService:
    settings = get_cached_settings()
    return ConversationService(
        provider=get_llm_provider(),
        memory_service=get_memory_service(),
        model_name=settings.ollama_model,
        temperature=settings.conversation_temperature,
        language=settings.conversation_language,
    )


@lru_cache(maxsize=1)
def get_audio_service() -> AudioService:
    settings = get_cached_settings()
    return AudioService(
        sample_rate=settings.audio_sample_rate,
        channels=settings.audio_channels,
        input_device=settings.audio_input_device,
        output_device=settings.audio_output_device,
    )


@lru_cache(maxsize=1)
def get_stt_service() -> FasterWhisperTranscriber:
    settings = get_cached_settings()
    return FasterWhisperTranscriber(
        model_name=settings.stt_model,
        device=settings.stt_device,
        compute_type=settings.stt_compute_type,
        language=settings.conversation_language,
        min_transcript_chars=settings.stt_min_transcript_chars,
        min_avg_logprob=settings.stt_min_avg_logprob,
        max_no_speech_prob=settings.stt_max_no_speech_prob,
    )


@lru_cache(maxsize=1)
def get_tts_service() -> PiperTTSProvider:
    settings = get_cached_settings()
    return PiperTTSProvider(
        voice_model_path=settings.tts_voice_model_path,
        voice_config_path=settings.tts_voice_config_path,
        use_cuda=settings.tts_use_cuda,
        output_device=settings.audio_output_device,
    )


@lru_cache(maxsize=1)
def get_vad_service() -> SileroVadService:
    return SileroVadService(sample_rate=get_cached_settings().audio_sample_rate)


@lru_cache(maxsize=1)
def get_wakeword_service() -> OpenWakeWordDetector:
    settings = get_cached_settings()
    return OpenWakeWordDetector(
        model_name=settings.wake_word_model_name,
        threshold=settings.wake_word_threshold,
        sample_rate=settings.audio_sample_rate,
        chunk_seconds=1.5,
        timeout_seconds=settings.wake_word_timeout_seconds,
        audio_service=get_audio_service(),
    )


@lru_cache(maxsize=1)
def get_voice_session_service() -> VoiceSessionService:
    return VoiceSessionService(
        settings=get_cached_settings(),
        conversation_service=get_conversation_service(),
        audio_service=get_audio_service(),
        stt_service=get_stt_service(),
        tts_service=get_tts_service(),
        wakeword_service=get_wakeword_service(),
        vad_service=get_vad_service(),
    )