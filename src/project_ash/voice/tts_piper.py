from __future__ import annotations

import subprocess
from pathlib import Path


class PiperTTS:
    def __init__(self, piper_exe: str = "piper", model_path: str | None = None) -> None:
        self.piper_exe = piper_exe
        self.model_path = model_path

    def speak(self, text: str, output_wav: str | Path | None = None) -> bool:
        if not self.model_path:
            return False

        cmd = [self.piper_exe, "--model", self.model_path]
        if output_wav is not None:
            cmd.extend(["--output_file", str(output_wav)])

        try:
            subprocess.run(cmd, input=text, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
