from __future__ import annotations

import asyncio

from app.schemas.chat import ChatRequest
from app.services.conversation_service import ConversationService
from app.services.memory_service import SessionMemoryService


class FakeLLMProvider:
    def __init__(self, reply: str = "I am here.") -> None:
        self.reply = reply
        self.last_messages = None

    async def chat(self, messages):  # type: ignore[override]
        self.last_messages = list(messages)
        return self.reply


def test_conversation_service_builds_prompt_and_saves_history() -> None:
    provider = FakeLLMProvider("Nice to talk with you.")
    memory = SessionMemoryService(limit=4)
    memory.append_turn("default", "hello", "hi there")
    service = ConversationService(
        provider=provider,
        memory_service=memory,
        model_name="llama3.1:8b-instruct",
    )

    response = asyncio.run(service.respond(ChatRequest(session_id="default", message="how are you?")))

    assert response.reply == "Nice to talk with you."
    assert response.history_size == 2
    assert provider.last_messages is not None
    assert provider.last_messages[0].role == "system"
    assert provider.last_messages[-1].content == "how are you?"