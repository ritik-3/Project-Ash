from __future__ import annotations

import asyncio

import numpy as np

from app.core.config import Settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.voice import WakeWordDetection
from app.services.audio_service import AudioService
from app.services.conversation_service import ConversationService
from app.services.memory_service import SessionMemoryService
from app.services.voice_session_service import VoiceSessionService


class FakeWakeWordService:
    def wait_for_wake_word(self) -> WakeWordDetection:  # type: ignore[override]
        return WakeWordDetection(detected=True, score=0.99, model_name="test")


class FakeVADService:
    def trim_speech(self, audio: np.ndarray) -> np.ndarray:  # type: ignore[override]
        return audio


class FakeSTTService:
    def transcribe(self, audio: np.ndarray) -> str:  # type: ignore[override]
        return "how are you"


class FakeTTSService:
    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str) -> None:  # type: ignore[override]
        self.spoken.append(text)


class FakeLLMProvider:
    async def chat(self, messages):  # type: ignore[override]
        return "I am doing well."


class CountingLLMProvider:
    def __init__(self, reply: str = "Echoed response") -> None:
        self.reply = reply
        self.calls = 0

    async def chat(self, messages):  # type: ignore[override]
        self.calls += 1
        return self.reply


def test_voice_turn_flow() -> None:
    settings = Settings.from_env()
    settings.utterance_record_seconds = 1.0

    memory = SessionMemoryService(limit=4)
    conversation_service = ConversationService(
        provider=FakeLLMProvider(),
        memory_service=memory,
        model_name="test-model",
    )

    voice_service = VoiceSessionService(
        settings=settings,
        conversation_service=conversation_service,
        audio_service=AudioService(sample_rate=16000),
        stt_service=FakeSTTService(),
        tts_service=FakeTTSService(),
        wakeword_service=FakeWakeWordService(),
        vad_service=FakeVADService(),
    )

    response = asyncio.run(voice_service.run_turn(session_id="default", wait_for_wake_word=True))

    assert response.status == "ok"
    assert response.transcript == "how are you"
    assert response.reply == "I am doing well."


def test_voice_turn_ignores_self_echo() -> None:
    settings = Settings.from_env()
    settings.utterance_record_seconds = 1.0

    memory = SessionMemoryService(limit=4)
    memory.append_turn("default", "hello", "I am doing well.")

    class EchoSTTService:
        def transcribe(self, audio: np.ndarray) -> str:  # type: ignore[override]
            return "I am doing well"

    llm = CountingLLMProvider(reply="Should not be used")
    conversation_service = ConversationService(
        provider=llm,
        memory_service=memory,
        model_name="test-model",
    )

    voice_service = VoiceSessionService(
        settings=settings,
        conversation_service=conversation_service,
        audio_service=AudioService(sample_rate=16000),
        stt_service=EchoSTTService(),
        tts_service=FakeTTSService(),
        wakeword_service=FakeWakeWordService(),
        vad_service=FakeVADService(),
    )

    response = asyncio.run(voice_service.run_turn(session_id="default", wait_for_wake_word=False))

    assert response.status == "timeout"
    assert "self-audio echo" in (response.detail or "")
    assert llm.calls == 0