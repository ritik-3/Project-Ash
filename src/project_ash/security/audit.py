from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from project_ash.memory.sqlite_store import SQLiteMemoryStore


class AuditLogger:
    def __init__(self, store: SQLiteMemoryStore) -> None:
        self.store = store

    def log(self, action: str, decision: str, metadata: dict[str, Any] | None = None) -> None:
        self.store.add_security_audit_event(
            action=action,
            decision=decision,
            metadata=metadata or {},
            created_at_utc=datetime.now(timezone.utc),
        )
