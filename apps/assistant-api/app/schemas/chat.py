from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    status: Literal["ok", "fallback"] = "ok"
    session_id: str
    reply: str
    history_size: int
    model: str