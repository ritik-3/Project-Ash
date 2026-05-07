from fastapi import APIRouter, Depends

from app.core.dependencies import get_audio_service, get_voice_session_service
from app.schemas.voice import VoiceTurnRequest, VoiceTurnResponse
from app.services.audio_service import AudioService
from app.services.voice_session_service import VoiceSessionService


router = APIRouter()


@router.get("/voice/devices")
async def list_audio_devices(
    audio_service: AudioService = Depends(get_audio_service),
) -> dict[str, list[dict[str, object]]]:
    return {"devices": audio_service.list_devices()}


@router.post("/voice/turn", response_model=VoiceTurnResponse)
async def voice_turn(
    request: VoiceTurnRequest,
    service: VoiceSessionService = Depends(get_voice_session_service),
) -> VoiceTurnResponse:
    return await service.run_turn(
        session_id=request.session_id,
        wait_for_wake_word=request.wait_for_wake_word,
        speak_reply=request.speak_reply,
    )