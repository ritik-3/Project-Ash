from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WakeWordEvent:
    detected: bool
    score: float


class OpenWakeWordDetector:
    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self._model = None

    def initialize(self) -> None:
        try:
            from openwakeword.model import Model
        except ImportError:
            self._model = None
            return
        self._model = Model()

    def detect_from_frame(self, audio_frame) -> WakeWordEvent:
        if self._model is None:
            return WakeWordEvent(detected=False, score=0.0)
        scores = self._model.predict(audio_frame)
        best = max(scores.values()) if scores else 0.0
        return WakeWordEvent(detected=best >= self.threshold, score=float(best))
