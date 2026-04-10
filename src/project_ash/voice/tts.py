from __future__ import annotations

import pyttsx3


class TextToSpeech:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled
        self._engine = pyttsx3.init() if enabled else None

    def speak(self, text: str) -> None:
        if not self.enabled or self._engine is None:
            return
        self._engine.say(text)
        self._engine.runAndWait()
