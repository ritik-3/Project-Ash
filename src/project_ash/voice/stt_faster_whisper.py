from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class WhisperTranscript:
    text: str
    confidence: float


class FasterWhisperSTT:
    def __init__(self, model_size: str = "small", device: str = "cuda", compute_type: str = "int8_float16") -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. Install optional local-ai dependencies first."
            ) from exc

        self._model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )

    def transcribe_file(self, audio_path: str | Path) -> WhisperTranscript:
        self._ensure_model()
        segments, info = self._model.transcribe(str(audio_path), beam_size=3, language=None)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        confidence = float(getattr(info, "language_probability", 0.0) or 0.0)
        return WhisperTranscript(text=text, confidence=confidence)
