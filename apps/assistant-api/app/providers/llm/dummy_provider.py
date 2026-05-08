from collections.abc import Sequence

from app.providers.llm.base import BaseLLMProvider
from app.schemas.chat import ChatMessage


class DummyProvider(BaseLLMProvider):
    """Simple test provider for local end-to-end runs.

    Returns a deterministic reply based on the last user message.
    """

    async def chat(self, messages: Sequence[ChatMessage]) -> str:
        # Find last user message
        last_user = ""
        for m in reversed(messages):
            if m.role.lower() == "user":
                last_user = m.content
                break

        if not last_user:
            return "Hello — this is a dummy assistant for testing."

        return f"[DUMMY RESPONSE] I received: {last_user}"
