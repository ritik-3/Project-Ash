"""Audio encoding/decoding utilities for browser-captured audio."""

from __future__ import annotations

import base64
import io
import struct

import numpy as np
import soundfile as sf


def decode_base64_audio(audio_base64: str) -> np.ndarray:
    """Decode base64-encoded WAV to numpy array.

    Args:
        audio_base64: Base64-encoded WAV file data.

    Returns:
        NumPy array of audio samples (float32, 16kHz assumed).

    Raises:
        ValueError: If decoding fails.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)
        audio_buffer = io.BytesIO(audio_bytes)
        audio, sr = sf.read(audio_buffer, dtype="float32")

        # Resample if needed (assume 16kHz target)
        if sr != 16000:
            import scipy.signal

            audio = scipy.signal.resample_poly(audio, 16000, sr)

        return audio.astype(np.float32)
    except Exception as exc:
        raise ValueError(f"Failed to decode audio: {exc}") from exc


def pcm_to_wav_bytes(pcm_data: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Encode PCM (float32) array to WAV format (bytes).

    Args:
        pcm_data: Float32 PCM audio data.
        sample_rate: Sample rate in Hz (default 16kHz).

    Returns:
        WAV file data as bytes.
    """
    num_channels = 1
    bits_per_sample = 16
    block_align = (num_channels * bits_per_sample) // 8
    byte_rate = sample_rate * block_align

    # Convert float32 to int16
    int16_data = np.clip(pcm_data * 32767, -32768, 32767).astype(np.int16)

    # Build WAV file structure
    wav_length = 36 + len(int16_data) * 2
    wav_buffer = io.BytesIO()

    # RIFF header
    wav_buffer.write(b"RIFF")
    wav_buffer.write(struct.pack("<I", wav_length))
    wav_buffer.write(b"WAVE")

    # fmt subchunk
    wav_buffer.write(b"fmt ")
    wav_buffer.write(struct.pack("<I", 16))  # subchunk1 size
    wav_buffer.write(struct.pack("<H", 1))  # PCM
    wav_buffer.write(struct.pack("<H", num_channels))
    wav_buffer.write(struct.pack("<I", sample_rate))
    wav_buffer.write(struct.pack("<I", byte_rate))
    wav_buffer.write(struct.pack("<H", block_align))
    wav_buffer.write(struct.pack("<H", bits_per_sample))

    # data subchunk
    wav_buffer.write(b"data")
    wav_buffer.write(struct.pack("<I", len(int16_data) * 2))
    wav_buffer.write(int16_data.tobytes())

    return wav_buffer.getvalue()
