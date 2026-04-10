from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model: str


class OllamaClient:
    def __init__(self, model: str = "llama3.1:8b-instruct-q4_K_M") -> None:
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.2) -> LLMResponse:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        command = ["ollama", "run", self.model, prompt]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return LLMResponse(text=result.stdout.strip(), model=self.model)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return LLMResponse(
                text=(
                    "Ollama is unavailable. Install and run Ollama, then pull the model with: "
                    f"ollama pull {self.model}"
                ),
                model=self.model,
            )

    def chat_json(self, payload: dict) -> LLMResponse:
        command = ["ollama", "chat", self.model]
        try:
            result = subprocess.run(
                command,
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                check=True,
            )
            return LLMResponse(text=result.stdout.strip(), model=self.model)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return LLMResponse(text="Ollama chat endpoint unavailable.", model=self.model)
