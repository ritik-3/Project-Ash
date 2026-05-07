from __future__ import annotations

import numpy as np
import scipy.signal
import sounddevice as sd


class AudioService:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        input_device: int | None = None,
        output_device: int | None = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.input_device = input_device
        self.output_device = output_device

    def record_duration(self, seconds: float) -> np.ndarray:
        frame_count = max(1, int(seconds * self.sample_rate))
        audio = sd.rec(
            frame_count,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            device=self.input_device,
        )
        sd.wait()
        return np.squeeze(audio)

    def record_until_silence(
        self,
        max_seconds: float,
        min_seconds: float = 0.8,
        silence_seconds: float = 0.7,
        silence_threshold: float = 0.012,
        chunk_seconds: float = 0.12,
    ) -> np.ndarray:
        chunk_frames = max(1, int(chunk_seconds * self.sample_rate))
        max_chunks = max(1, int(max_seconds / chunk_seconds))

        chunks: list[np.ndarray] = []
        captured_seconds = 0.0
        silent_seconds = 0.0

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            device=self.input_device,
            blocksize=chunk_frames,
        ) as stream:
            for _ in range(max_chunks):
                chunk, _overflowed = stream.read(chunk_frames)
                chunk = np.asarray(chunk, dtype=np.float32)

                if chunk.ndim > 1 and chunk.shape[1] > 1:
                    chunk_mono = np.mean(chunk, axis=1)
                else:
                    chunk_mono = np.squeeze(chunk)

                chunks.append(chunk_mono)
                captured_seconds += chunk_seconds

                # RMS gate detects end-of-utterance after minimum capture time.
                rms = float(np.sqrt(np.mean(np.square(chunk_mono)))) if chunk_mono.size else 0.0
                if captured_seconds < min_seconds:
                    continue

                if rms < silence_threshold:
                    silent_seconds += chunk_seconds
                else:
                    silent_seconds = 0.0

                if silent_seconds >= silence_seconds:
                    break

        if not chunks:
            return np.zeros(0, dtype=np.float32)

        return np.concatenate(chunks, axis=0)

    def play(self, audio: np.ndarray, sample_rate: int) -> None:
        sd.play(audio, sample_rate, device=self.output_device)
        sd.wait()

    @staticmethod
    def list_devices() -> list[dict[str, object]]:
        devices = sd.query_devices()
        result: list[dict[str, object]] = []
        for index, device in enumerate(devices):
            result.append(
                {
                    "index": index,
                    "name": str(device.get("name", "unknown")),
                    "max_input_channels": int(device.get("max_input_channels", 0)),
                    "max_output_channels": int(device.get("max_output_channels", 0)),
                    "default_samplerate": float(device.get("default_samplerate", 0.0)),
                }
            )
        return result

    @staticmethod
    def clip_audio(audio: np.ndarray) -> np.ndarray:
        return np.clip(audio, -1.0, 1.0)

    @staticmethod
    def resample(audio: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
        if source_rate == target_rate:
            return audio
        return scipy.signal.resample_poly(audio, target_rate, source_rate)