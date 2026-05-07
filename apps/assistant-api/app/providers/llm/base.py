from typing import Protocol, Sequence

from app.schemas.chat import ChatMessage


class BaseLLMProvider(Protocol):
    async def chat(self, messages: Sequence[ChatMessage]) -> str:
        raise NotImplementedError
