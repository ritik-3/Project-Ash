from __future__ import annotations

import re
import logging
import tempfile
import threading
import wave
from pathlib import Path

import sounddevice as sd
import soundfile as sf
from huggingface_hub import hf_hub_download

from app.providers.tts.base import BaseTTSProvider


logger = logging.getLogger(__name__)


_VOICE_PRESET_RE = re.compile(
    r"^(?P<locale>[a-z]{2}_[A-Z]{2})-(?P<voice>[a-z0-9_]+)-(?P<quality>low|medium|high|x_low)$"
)


def _build_hf_filenames(preset: str) -> tuple[str, str]:
    match = _VOICE_PRESET_RE.match(preset.strip())
    if not match:
        raise ValueError(
            "Invalid PIPER_VOICE_PRESET format. Expected locale-voice-quality, for example en_US-lessac-medium."
        )

    locale = match.group("locale")
    voice = match.group("voice")
    quality = match.group("quality")
    language = locale.split("_", maxsplit=1)[0].lower()
    base = f"{language}/{locale}/{voice}/{quality}/{locale}-{voice}-{quality}"
    return f"{base}.onnx", f"{base}.onnx.json"


class PiperTTSProvider(BaseTTSProvider):
    def __init__(
        self,
        voice_model_path: Path | None,
        voice_config_path: Path | None = None,
        voice_preset: str | None = None,
        voice_cache_dir: Path | None = None,
        use_cuda: bool = False,
        output_device: int | None = None,
    ) -> None:
        self.voice_model_path = voice_model_path
        self.voice_config_path = voice_config_path
        self.voice_preset = voice_preset
        self.voice_cache_dir = voice_cache_dir or Path("models/piper")
        self.use_cuda = use_cuda
        self.output_device = output_device
        self._voice = None
        self._speak_lock = threading.Lock()

    def _load_voice(self):
        model_path = self.voice_model_path
        config_path = self.voice_config_path

        if model_path is None and self.voice_preset:
            try:
                model_filename, config_filename = _build_hf_filenames(self.voice_preset)
                self.voice_cache_dir.mkdir(parents=True, exist_ok=True)
                model_path = Path(
                    hf_hub_download(
                        repo_id="rhasspy/piper-voices",
                        filename=model_filename,
                        revision="v1.0.0",
                        local_dir=str(self.voice_cache_dir),
                        local_dir_use_symlinks=False,
                    )
                )
                config_path = Path(
                    hf_hub_download(
                        repo_id="rhasspy/piper-voices",
                        filename=config_filename,
                        revision="v1.0.0",
                        local_dir=str(self.voice_cache_dir),
                        local_dir_use_symlinks=False,
                    )
                )
            except Exception as exc:  # pragma: no cover - network/runtime fallback
                logger.warning("Failed to download Piper preset '%s': %s", self.voice_preset, exc)
                return None

        if model_path is None:
            return None

        from piper.voice import PiperVoice

        try:
            return PiperVoice.load(
                model_path,
                config_path=config_path,
                use_cuda=self.use_cuda,
            )
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.warning("Failed to load Piper voice from %s: %s", model_path, exc)
            return None

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