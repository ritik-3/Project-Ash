from app.providers.llm.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    async def chat(self, prompt: str) -> str:
        raise NotImplementedError("Ollama chat integration will be implemented here.")
