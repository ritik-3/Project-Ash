from __future__ import annotations

import subprocess
import tempfile
import winsound
from pathlib import Path


class PiperTTS:
    def __init__(self, piper_exe: str = "piper", model_path: str | None = None) -> None:
        self.piper_exe = piper_exe
        self.model_path = model_path

    def speak(self, text: str, output_wav: str | Path | None = None) -> bool:
        if not self.model_path:
            return False

        temp_file: Path | None = None
        target_file = Path(output_wav) if output_wav is not None else None
        if target_file is None:
            temp_file = Path(tempfile.gettempdir()) / "project_ash_tts.wav"
            target_file = temp_file

        cmd = [self.piper_exe, "--model", self.model_path, "--output_file", str(target_file)]

        try:
            subprocess.run(cmd, input=text, text=True, check=True)
            winsound.PlaySound(str(target_file), winsound.SND_FILENAME)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        finally:
            if temp_file is not None:
                try:
                    temp_file.unlink(missing_ok=True)
                except Exception:
                    pass
