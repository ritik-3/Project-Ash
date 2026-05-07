from collections.abc import Sequence

import httpx

from app.providers.llm.base import BaseLLMProvider
from app.schemas.chat import ChatMessage


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 180.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def chat(self, messages: Sequence[ChatMessage]) -> str:
        chat_payload = {
            "model": self.model,
            "messages": [message.model_dump(mode="json") for message in messages],
            "stream": False,
            "options": {
                "temperature": 0.7,
            },
        }

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            response = await client.post("/api/chat", json=chat_payload)

            if response.status_code == 404:
                generate_payload = {
                    "model": self.model,
                    "prompt": self._to_prompt(messages),
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                    },
                }
                response = await client.post("/api/generate", json=generate_payload)

            response.raise_for_status()
            data = response.json()

        message = data.get("message", {})
        content = str(message.get("content", data.get("response", ""))).strip()
        if not content:
            raise RuntimeError("Ollama returned an empty response")
        return content

    @staticmethod
    def _to_prompt(messages: Sequence[ChatMessage]) -> str:
        chunks: list[str] = []
        for msg in messages:
            role = msg.role.upper()
            chunks.append(f"{role}: {msg.content}")
        chunks.append("ASSISTANT:")
        return "\n\n".join(chunks)
