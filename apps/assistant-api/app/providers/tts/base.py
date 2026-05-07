from typing import Protocol


class BaseTTSProvider(Protocol):
    def speak(self, text: str) -> None:
        raise NotImplementedError