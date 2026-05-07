from __future__ import annotations

import asyncio
import re
import logging
from difflib import SequenceMatcher

from app.core.config import Settings
from app.schemas.chat import ChatRequest
from app.schemas.voice import VoiceTurnResponse
from app.services.audio_service import AudioService
from app.services.conversation_service import ConversationService
from app.providers.stt.faster_whisper_provider import FasterWhisperTranscriber
from app.providers.tts.piper_provider import PiperTTSProvider
from app.providers.vad.silero_provider import SileroVadService
from app.providers.wakeword.openwakeword_provider import OpenWakeWordDetector

logger = logging.getLogger(__name__)


class VoiceSessionService:
    def __init__(
        self,
        settings: Settings,
        conversation_service: ConversationService,
        audio_service: AudioService,
        stt_service: FasterWhisperTranscriber,
        tts_service: PiperTTSProvider,
        wakeword_service: OpenWakeWordDetector,
        vad_service: SileroVadService,
    ) -> None:
        self.settings = settings
        self.conversation_service = conversation_service
        self.audio_service = audio_service
        self.stt_service = stt_service
        self.tts_service = tts_service
        self.wakeword_service = wakeword_service
        self.vad_service = vad_service

    @staticmethod
    def _normalize_for_echo(text: str) -> str:
        lowered = text.lower().strip()
        lowered = re.sub(r"\s+", " ", lowered)
        lowered = re.sub(r"[^a-z0-9\s]", "", lowered)
        return lowered.strip()

    def _looks_like_self_echo(self, session_id: str, transcript: str) -> bool:
        normalized_transcript = self._normalize_for_echo(transcript)
        if len(normalized_transcript) < 8:
            return False

        recent_turns = self.conversation_service.memory_service.recent_turns(session_id)
        recent_assistant_messages = [turn.assistant for turn in recent_turns[-3:]]

        for assistant_message in recent_assistant_messages:
            normalized_assistant = self._normalize_for_echo(assistant_message)
            if len(normalized_assistant) < 8:
                continue

            if normalized_transcript == normalized_assistant:
                return True

            if normalized_transcript in normalized_assistant or normalized_assistant in normalized_transcript:
                if min(len(normalized_transcript), len(normalized_assistant)) >= 16:
                    return True

            ratio = SequenceMatcher(None, normalized_transcript, normalized_assistant).ratio()
            if ratio >= 0.82:
                return True

        return False

    async def run_turn(
        self,
        session_id: str = "default",
        wait_for_wake_word: bool = True,
        speak_reply: bool = True,
    ) -> VoiceTurnResponse:
        try:
            wake_word_detected = True
            wake_word_score = 0.0

            if wait_for_wake_word:
                detection = await asyncio.to_thread(self.wakeword_service.wait_for_wake_word)
                wake_word_detected = detection.detected
                wake_word_score = detection.score
                if not detection.detected:
                    return VoiceTurnResponse(
                        status="timeout",
                        session_id=session_id,
                        wake_word_detected=False,
                        wake_word_score=0.0,
                        detail="Wake word timeout reached before activation.",
                    )

            try:
                audio = await asyncio.to_thread(
                    self.audio_service.record_until_silence,
                    self.settings.utterance_record_seconds,
                    self.settings.utterance_min_record_seconds,
                    self.settings.utterance_silence_seconds,
                    self.settings.utterance_silence_threshold,
                    self.settings.utterance_chunk_seconds,
                )
            except Exception as record_exc:  # pragma: no cover - runtime fallback
                logger.warning("Adaptive recording failed; falling back to fixed duration: %s", record_exc)
                audio = await asyncio.to_thread(self.audio_service.record_duration, self.settings.utterance_record_seconds)
            audio = await asyncio.to_thread(self.vad_service.trim_speech, audio)
            transcript = await asyncio.to_thread(self.stt_service.transcribe, audio)

            if not transcript.strip():
                return VoiceTurnResponse(
                    status="error",
                    session_id=session_id,
                    wake_word_detected=wake_word_detected,
                    wake_word_score=wake_word_score,
                    detail="No speech was detected after wake word activation.",
                )

            if self._looks_like_self_echo(session_id, transcript):
                return VoiceTurnResponse(
                    status="timeout",
                    session_id=session_id,
                    wake_word_detected=wake_word_detected,
                    wake_word_score=wake_word_score,
                    detail="Detected self-audio echo and ignored this turn.",
                )

            reply = await self.conversation_service.respond(
                ChatRequest(session_id=session_id, message=transcript)
            )
            tts_warning: str | None = None
            if speak_reply:
                try:
                    await asyncio.to_thread(self.tts_service.speak, reply.reply)
                except Exception as tts_exc:  # pragma: no cover - runtime audio fallback
                    logger.warning("TTS playback failed, continuing without spoken output: %s", tts_exc)
                    tts_warning = f"TTS playback failed: {tts_exc}"

            return VoiceTurnResponse(
                status=reply.status,  # type: ignore[arg-type]
                session_id=session_id,
                wake_word_detected=wake_word_detected,
                wake_word_score=wake_word_score,
                transcript=transcript,
                reply=reply.reply,
                history_size=reply.history_size,
                model=reply.model,
                detail=tts_warning,
            )
        except Exception as exc:  # pragma: no cover - runtime safety fallback
            logger.exception("Voice turn failed")
            return VoiceTurnResponse(
                status="error",
                session_id=session_id,
                detail=str(exc),
            )