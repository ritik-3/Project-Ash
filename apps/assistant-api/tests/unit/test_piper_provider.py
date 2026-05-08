from __future__ import annotations

import pytest

from app.providers.tts.piper_provider import _build_hf_filenames


def test_build_hf_filenames_supports_us_medium_voice() -> None:
    model_filename, config_filename = _build_hf_filenames("en_US-lessac-medium")

    assert model_filename == "en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    assert config_filename == "en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"


@pytest.mark.parametrize("preset", ["", "lessac-medium", "en_US-lessac", "en_US-lessac-voice"])
def test_build_hf_filenames_rejects_invalid_presets(preset: str) -> None:
    with pytest.raises(ValueError):
        _build_hf_filenames(preset)