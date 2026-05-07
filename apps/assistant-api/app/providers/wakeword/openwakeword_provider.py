from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import openwakeword
from openwakeword.model import Model
from openwakeword.utils import download_models

from app.providers.wakeword.base import BaseWakeWordDetector
from app.schemas.voice import WakeWordDetection
from app.services.audio_service import AudioService


class OpenWakeWordDetector(BaseWakeWordDetector):
    def __init__(
        self,
        model_name: str,
        threshold: float,
        sample_rate: int,
        chunk_seconds: float,
        timeout_seconds: float,
        audio_service: AudioService,
    ) -> None:
        self.model_name = model_name
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.chunk_seconds = chunk_seconds
        self.timeout_seconds = timeout_seconds
        self.audio_service = audio_service
        self.model = Model(wakeword_models=[self._ensure_model(model_name)], inference_framework="onnx")

    @staticmethod
    def _ensure_model(model_name: str) -> str:
        if model_name not in openwakeword.MODELS:
            raise ValueError(f"Unknown openWakeWord model: {model_name}")

        model_path = Path(openwakeword.MODELS[model_name]["model_path"]).with_suffix(".onnx")
        if not model_path.exists():
            download_models([f"{model_name}_v0.1"], target_directory=str(model_path.parent))

        if not model_path.exists():
            raise FileNotFoundError(f"Unable to locate wake word model: {model_path}")

        return str(model_path)

    def _predict(self, audio: np.ndarray) -> float:
        scores = self.model.predict(
            audio.astype(np.float32),
            threshold={self.model_name: self.threshold},
        )
        return float(scores.get(self.model_name, 0.0))

    def wait_for_wake_word(self) -> WakeWordDetection:
        deadline = time.monotonic() + self.timeout_seconds

        while time.monotonic() < deadline:
            audio = self.audio_service.record_duration(self.chunk_seconds)
            score = self._predict(audio)
            if score >= self.threshold:
                return WakeWordDetection(detected=True, score=score, model_name=self.model_name)

        return WakeWordDetection(detected=False, score=0.0, model_name=self.model_name)