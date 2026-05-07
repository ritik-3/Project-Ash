from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

from app.providers.stt.base import BaseSTTProvider


class FasterWhisperTranscriber(BaseSTTProvider):
    def __init__(
        self,
        model_name: str,
        device: str = "auto",
        compute_type: str = "int8",
        language: str = "en",
        min_transcript_chars: int = 5,
        min_avg_logprob: float = -1.0,
        max_no_speech_prob: float = 0.55,
    ) -> None:
        self.model_name = model_name
        self.language = language
        self.compute_type = compute_type
        self.device = device
        self.min_transcript_chars = min_transcript_chars
        self.min_avg_logprob = min_avg_logprob
        self.max_no_speech_prob = max_no_speech_prob
        try:
            self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
        except Exception as exc:
            error_text = str(exc).lower()
            if device != "cpu" and ("cublas" in error_text or "cuda" in error_text):
                self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
                self.device = "cpu"
            else:
                raise

    def transcribe(self, audio: np.ndarray | str | Path) -> str:
        if isinstance(audio, np.ndarray) and audio.size == 0:
            return ""

        try:
            segments, _info = self.model.transcribe(
                audio,
                language=self.language,
                vad_filter=True,
            )
        except RuntimeError as exc:
            error_text = str(exc).lower()
            if self.device != "cpu" and ("cublas" in error_text or "cuda" in error_text):
                self.model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
                self.device = "cpu"
                segments, _info = self.model.transcribe(
                    audio,
                    language=self.language,
                    vad_filter=True,
                )
            else:
                raise

        segment_list = list(segments)
        transcript = " ".join(segment.text.strip() for segment in segment_list).strip()

        if len(transcript) < self.min_transcript_chars:
            return ""

        avg_logprobs = [float(getattr(segment, "avg_logprob", 0.0)) for segment in segment_list if getattr(segment, "avg_logprob", None) is not None]
        if avg_logprobs and (sum(avg_logprobs) / len(avg_logprobs)) < self.min_avg_logprob:
            return ""

        no_speech_probs = [float(getattr(segment, "no_speech_prob", 0.0)) for segment in segment_list if getattr(segment, "no_speech_prob", None) is not None]
        if no_speech_probs and (sum(no_speech_probs) / len(no_speech_probs)) > self.max_no_speech_prob:
            return ""

        return transcript