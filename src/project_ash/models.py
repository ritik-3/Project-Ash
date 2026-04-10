from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class InputMode(str, Enum):
    TEXT = "text"
    VOICE = "voice"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChannelType(str, Enum):
    TELEGRAM = "telegram"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"


class JobSource(str, Enum):
    DIRECT = "direct"
    SCHEDULED = "scheduled"
    AUTONOMOUS_RULE = "autonomous_rule"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class ApprovalDecision(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class IntentType(str, Enum):
    OPEN_APP = "open_app"
    OPEN_WEBSITE = "open_website"
    SCREEN_SUMMARY = "screen_summary"
    DRAFT_MESSAGE = "draft_message"
    CREATE_SHEET = "create_sheet"
    ADD_SHEET_ROW = "add_sheet_row"
    SEARCH_WEB = "search_web"
    DRAFT_GMAIL = "draft_gmail"
    CREATE_GOOGLE_SHEET = "create_google_sheet"
    ADD_GOOGLE_SHEET_ROW = "add_google_sheet_row"
    TYPE_IN_ACTIVE_WINDOW = "type_in_active_window"
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
    execution_mode: str = "immediate"
    tags: list[str] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    user_goal: str
    steps: list[PlanStep] = Field(default_factory=list)


class ChannelEnvelope(BaseModel):
    envelope_id: str
    channel_type: ChannelType
    channel_user_id: str
    channel_conversation_id: str
    timestamp_utc: datetime
    message_text: str
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobRecord(BaseModel):
    job_id: str
    owner_user_id: str
    source: JobSource
    intent_text: str
    plan_snapshot: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel
    status: JobStatus
    run_at_utc: datetime
    retry_count: int = 0
    last_error: str | None = None


class ScheduleRecord(BaseModel):
    schedule_id: str
    owner_user_id: str
    intent_text: str
    run_at_utc: datetime
    recurrence: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalRecord(BaseModel):
    approval_id: str
    job_id: str
    required_for_risk: RiskLevel
    prompt_summary: str
    decision: ApprovalDecision | None = None
    decided_by: str | None = None
    decided_at_utc: datetime | None = None


class SkillManifest(BaseModel):
    name: str
    version: str
    description: str
    actions_exposed: list[str] = Field(default_factory=list)
    required_permissions: list[str] = Field(default_factory=list)
    risk_level_default: RiskLevel = RiskLevel.MEDIUM
    external_scopes: list[str] = Field(default_factory=list)
    network_policy: str = "none"
    requires_confirmation: bool = True
    maintainer_signature: str | None = None


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str


class StepResult(BaseModel):
    step_id: int
    success: bool
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    success: bool
    summary: str
    step_results: list[StepResult] = Field(default_factory=list)
