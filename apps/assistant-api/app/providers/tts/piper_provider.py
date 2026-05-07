from __future__ import annotations

import tempfile
import threading
import wave
from pathlib import Path

import sounddevice as sd
import soundfile as sf

from app.providers.tts.base import BaseTTSProvider


class PiperTTSProvider(BaseTTSProvider):
    def __init__(
        self,
        voice_model_path: Path | None,
        voice_config_path: Path | None = None,
        use_cuda: bool = False,
        output_device: int | None = None,
    ) -> None:
        self.voice_model_path = voice_model_path
        self.voice_config_path = voice_config_path
        self.use_cuda = use_cuda
        self.output_device = output_device
        self._voice = None
        self._speak_lock = threading.Lock()

    def _load_voice(self):
        if self.voice_model_path is None:
            return None

        from piper.voice import PiperVoice

        return PiperVoice.load(
            self.voice_model_path,
            config_path=self.voice_config_path,
            use_cuda=self.use_cuda,
        )

    def _speak_with_sapi(self, text: str) -> None:
        try:
            import pythoncom  # type: ignore
            import win32com.client  # type: ignore
        except Exception as exc:  # pragma: no cover - platform fallback
            raise RuntimeError("No Piper voice model configured and Windows SAPI fallback is unavailable") from exc

        # SAPI is COM-based and is sensitive to thread apartment setup.
        pythoncom.CoInitialize()
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
        finally:
            pythoncom.CoUninitialize()

    def speak(self, text: str) -> None:
        if not text.strip():
            return

        # Serialize playback to avoid concurrent access to audio output/SAPI.
        with self._speak_lock:
            if self._voice is None:
                self._voice = self._load_voice()

            if self._voice is None:
                self._speak_with_sapi(text)
                return

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = Path(temp_file.name)

            try:
                with wave.open(str(temp_path), "wb") as wav_file:
                    self._voice.synthesize_wav(text, wav_file)

                audio, sample_rate = sf.read(str(temp_path), dtype="float32")
                sd.play(audio, sample_rate, device=self.output_device)
                sd.wait()
            finally:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass