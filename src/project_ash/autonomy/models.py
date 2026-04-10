from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ScheduleSpec(BaseModel):
    owner_user_id: str
    intent_text: str
    run_at_utc: datetime
    recurrence: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
