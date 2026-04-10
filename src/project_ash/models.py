from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class InputMode(str, Enum):
    TEXT = "text"
    VOICE = "voice"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IntentType(str, Enum):
    OPEN_APP = "open_app"
    OPEN_WEBSITE = "open_website"
    SCREEN_SUMMARY = "screen_summary"
    DRAFT_MESSAGE = "draft_message"
    CREATE_SHEET = "create_sheet"
    ADD_SHEET_ROW = "add_sheet_row"
    SEARCH_WEB = "search_web"
    UNKNOWN = "unknown"


class UserInput(BaseModel):
    mode: InputMode = InputMode.TEXT
    text: str


class ParsedIntent(BaseModel):
    intent: IntentType
    entities: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    normalized_text: str


class PlanStep(BaseModel):
    step_id: int
    action: str
    params: dict[str, Any] = Field(default_factory=dict)
    risk: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False


class ExecutionPlan(BaseModel):
    user_goal: str
    steps: list[PlanStep] = Field(default_factory=list)


class StepResult(BaseModel):
    step_id: int
    success: bool
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    success: bool
    summary: str
    step_results: list[StepResult] = Field(default_factory=list)
