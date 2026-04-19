from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat(self, prompt: str) -> str:
        raise NotImplementedError
