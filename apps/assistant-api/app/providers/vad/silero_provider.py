from __future__ import annotations

import numpy as np
import torch
from silero_vad import get_speech_timestamps, load_silero_vad

from app.providers.vad.base import BaseVadService


class SileroVadService(BaseVadService):
    def __init__(self, threshold: float = 0.5, sample_rate: int = 16000, speech_pad_seconds: float = 0.2) -> None:
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.speech_pad_seconds = speech_pad_seconds
        self.model = load_silero_vad(onnx=True)

    def trim_speech(self, audio: np.ndarray) -> np.ndarray:
        if audio.size == 0:
            return audio

        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        tensor = torch.from_numpy(audio.astype(np.float32))
        timestamps = get_speech_timestamps(
            tensor,
            self.model,
            threshold=self.threshold,
            sampling_rate=self.sample_rate,
            return_seconds=False,
        )

        if not timestamps:
            return np.zeros(0, dtype=np.float32)

        start_sample = max(0, int(timestamps[0]["start"] - self.speech_pad_seconds * self.sample_rate))
        end_sample = min(len(audio), int(timestamps[-1]["end"] + self.speech_pad_seconds * self.sample_rate))
        return audio[start_sample:end_sample]