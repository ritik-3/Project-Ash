from fastapi import APIRouter

from app.core.dependencies import get_cached_settings
from app.schemas.common import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_cached_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        model=settings.ollama_model,
        voice_model_ready=bool(settings.tts_voice_model_path or settings.tts_voice_preset),
        wake_word_model=settings.wake_word_model_name,
    )
