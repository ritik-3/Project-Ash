from __future__ import annotations

import logging

from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.services.memory_service import SessionMemoryService

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(
        self,
        provider,
        memory_service: SessionMemoryService,
        model_name: str,
        temperature: float = 0.7,
        language: str = "en",
    ) -> None:
        self.provider = provider
        self.memory_service = memory_service
        self.model_name = model_name
        self.temperature = temperature
        self.language = language

    @staticmethod
    def system_prompt() -> str:
        return (
            "You are Ash, a female voice-first assistant. "
            "You are confident, friendly, slightly sarcastic, and conversational. "
            "Phase 1 allows only basic conversation. Do not claim you can execute tasks, "
            "open apps, browse the web, or control the computer. Keep replies natural, "
            "clear, and spoken-friendly. Ask a clarifying question when the user is unclear. "
            "Keep answers concise unless the user asks for more detail."
        )

    def build_messages(self, session_id: str, user_message: str) -> list[ChatMessage]:
        messages = [ChatMessage(role="system", content=self.system_prompt())]
        messages.extend(self.memory_service.to_messages(session_id))
        messages.append(ChatMessage(role="user", content=user_message))
        return messages

    async def respond(self, request: ChatRequest) -> ChatResponse:
        messages = self.build_messages(request.session_id, request.message)

        try:
            reply = await self.provider.chat(messages)
            status = "ok"
        except Exception as exc:  # pragma: no cover - exercised in runtime fallback
            logger.exception("LLM request failed; using fallback reply")
            reply = (
                "I hit a local model problem, but I am still here. "
                "Please try again in a moment."
            )
            status = "fallback"
            reply = f"{reply}"
            logger.debug("Fallback reason: %s", exc)

        reply = reply.strip()
        history_size = self.memory_service.append_turn(request.session_id, request.message, reply)

        return ChatResponse(
            status=status,  # type: ignore[arg-type]
            session_id=request.session_id,
            reply=reply,
            history_size=history_size,
            model=self.model_name,
        )