from __future__ import annotations

from datetime import datetime, timezone

from project_ash.memory.sqlite_store import SQLiteMemoryStore
from project_ash.models import JobRecord, JobSource, JobStatus, RiskLevel


class JobQueue:
    def __init__(self, store: SQLiteMemoryStore) -> None:
        self.store = store

    def enqueue(self, owner_user_id: str, intent_text: str, run_at_utc: datetime | None = None) -> JobRecord:
        return self.store.create_job(
            owner_user_id=owner_user_id,
            source=JobSource.SCHEDULED,
            intent_text=intent_text,
            plan_snapshot={},
            risk_level=RiskLevel.MEDIUM,
            run_at_utc=run_at_utc or datetime.now(timezone.utc),
            status=JobStatus.QUEUED,
        )

    def next_job(self) -> JobRecord | None:
        return self.store.claim_next_queued_job()
