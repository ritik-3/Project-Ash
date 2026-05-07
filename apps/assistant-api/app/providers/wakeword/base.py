from typing import Protocol

from app.schemas.voice import WakeWordDetection


class BaseWakeWordDetector(Protocol):
    def wait_for_wake_word(self) -> WakeWordDetection:
        raise NotImplementedError