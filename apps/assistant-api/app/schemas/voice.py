from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class WakeWordDetection(BaseModel):
    detected: bool
    score: float
    model_name: str


class VoiceTurnRequest(BaseModel):
    session_id: str = "default"
    wait_for_wake_word: bool = True
    speak_reply: bool = True


class VoiceTurnWithAudioRequest(BaseModel):
    """Voice turn with browser-captured base64 audio."""

    session_id: str = "default"
    audio_base64: str = Field(min_length=1, description="Base64-encoded WAV audio data")
    speak_reply: bool = True


class VoiceTurnResponse(BaseModel):
    status: Literal["ok", "timeout", "error", "fallback"]
    session_id: str
    wake_word_detected: bool = False
    wake_word_score: float = 0.0
    transcript: str = ""
    reply: str = ""
    history_size: int = 0
    model: str = ""
    detail: str | None = None