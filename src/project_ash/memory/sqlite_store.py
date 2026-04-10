from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from project_ash.autonomy.models import ScheduleSpec
from project_ash.models import (
    ApprovalDecision,
    ApprovalRecord,
    JobRecord,
    JobSource,
    JobStatus,
    RiskLevel,
    ScheduleRecord,
    SkillManifest,
)


@dataclass
class TaskLogRecord:
    goal: str
    summary: str
    success: bool


class SQLiteMemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    success INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS channel_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_type TEXT NOT NULL,
                    channel_user_id TEXT NOT NULL,
                    channel_conversation_id TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    intent_text TEXT NOT NULL,
                    plan_snapshot TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    run_at_utc TEXT NOT NULL,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS job_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    attempted_at_utc TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    error TEXT,
                    FOREIGN KEY(job_id) REFERENCES jobs(job_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    intent_text TEXT NOT NULL,
                    run_at_utc TEXT NOT NULL,
                    recurrence TEXT,
                    metadata TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    required_for_risk TEXT NOT NULL,
                    prompt_summary TEXT NOT NULL,
                    decision TEXT,
                    decided_by TEXT,
                    decided_at_utc TEXT,
                    FOREIGN KEY(job_id) REFERENCES jobs(job_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS skills_registry (
                    name TEXT PRIMARY KEY,
                    enabled INTEGER NOT NULL,
                    manifest_json TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS skill_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS security_audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at_utc TEXT NOT NULL,
                    action TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_run_at ON jobs(status, run_at_utc)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_approvals_job_decision ON approvals(job_id, decision)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_security_audit_created_at ON security_audit_events(created_at_utc)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_name_enabled ON skills_registry(name, enabled)")
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS task_logs_fts
                USING fts5(goal, summary, content='task_logs', content_rowid='id')
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS task_logs_ai AFTER INSERT ON task_logs BEGIN
                    INSERT INTO task_logs_fts(rowid, goal, summary)
                    VALUES (new.id, new.goal, new.summary);
                END
                """
            )

    def add_task_log(self, record: TaskLogRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO task_logs(created_at, goal, summary, success) VALUES (?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), record.goal, record.summary, int(record.success)),
            )

    def search_task_logs(self, query: str, limit: int = 5) -> list[sqlite3.Row]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT l.*
                FROM task_logs_fts f
                JOIN task_logs l ON l.id = f.rowid
                WHERE task_logs_fts MATCH ?
                ORDER BY l.id DESC
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        return rows

    def create_job(
        self,
        owner_user_id: str,
        source: JobSource,
        intent_text: str,
        plan_snapshot: dict[str, Any],
        risk_level: RiskLevel,
        run_at_utc: datetime,
        status: JobStatus = JobStatus.QUEUED,
    ) -> JobRecord:
        job_id = str(uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs(job_id, owner_user_id, source, intent_text, plan_snapshot, risk_level, status, run_at_utc, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    job_id,
                    owner_user_id,
                    source.value,
                    intent_text,
                    json.dumps(plan_snapshot, ensure_ascii=True),
                    risk_level.value,
                    status.value,
                    run_at_utc.isoformat(),
                ),
            )
        return JobRecord(
            job_id=job_id,
            owner_user_id=owner_user_id,
            source=source,
            intent_text=intent_text,
            plan_snapshot=plan_snapshot,
            risk_level=risk_level,
            status=status,
            run_at_utc=run_at_utc,
            retry_count=0,
            last_error=None,
        )

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return self._row_to_job(row) if row else None

    def list_jobs(self, limit: int = 100) -> list[JobRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM jobs ORDER BY run_at_utc DESC LIMIT ?", (limit,)).fetchall()
        return [self._row_to_job(row) for row in rows]

    def claim_next_queued_job(self) -> JobRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM jobs
                WHERE status = ? AND run_at_utc <= ?
                ORDER BY run_at_utc ASC
                LIMIT 1
                """,
                (JobStatus.QUEUED.value, now),
            ).fetchone()
            if not row:
                return None
            conn.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (JobStatus.RUNNING.value, row["job_id"]))
        claimed = dict(row)
        claimed["status"] = JobStatus.RUNNING.value
        return self._row_to_job(claimed)

    def update_job_status(self, job_id: str, status: JobStatus, last_error: str | None = None) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE jobs SET status = ?, last_error = ? WHERE job_id = ?",
                (status.value, last_error, job_id),
            )
            return cur.rowcount > 0

    def increment_job_retry(self, job_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE jobs SET retry_count = retry_count + 1, status = ? WHERE job_id = ?",
                (JobStatus.QUEUED.value, job_id),
            )
            return cur.rowcount > 0

    def create_approval(self, job_id: str, required_for_risk: RiskLevel, prompt_summary: str) -> ApprovalRecord:
        approval_id = str(uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO approvals(approval_id, job_id, required_for_risk, prompt_summary)
                VALUES (?, ?, ?, ?)
                """,
                (approval_id, job_id, required_for_risk.value, prompt_summary),
            )
        return ApprovalRecord(
            approval_id=approval_id,
            job_id=job_id,
            required_for_risk=required_for_risk,
            prompt_summary=prompt_summary,
        )

    def set_approval_decision(self, job_id: str, decision: ApprovalDecision, decided_by: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE approvals
                SET decision = ?, decided_by = ?, decided_at_utc = ?
                WHERE job_id = ? AND decision IS NULL
                """,
                (decision.value, decided_by, datetime.now(timezone.utc).isoformat(), job_id),
            )
            return cur.rowcount > 0

    def list_pending_approvals(self) -> list[ApprovalRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM approvals WHERE decision IS NULL ORDER BY rowid DESC").fetchall()
        return [self._row_to_approval(row) for row in rows]

    def get_latest_approval(self, job_id: str) -> ApprovalRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM approvals WHERE job_id = ? ORDER BY rowid DESC LIMIT 1",
                (job_id,),
            ).fetchone()
        return self._row_to_approval(row) if row else None

    def create_schedule(self, spec: ScheduleSpec) -> ScheduleRecord:
        schedule_id = str(uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO schedules(schedule_id, owner_user_id, intent_text, run_at_utc, recurrence, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    schedule_id,
                    spec.owner_user_id,
                    spec.intent_text,
                    spec.run_at_utc.isoformat(),
                    spec.recurrence,
                    json.dumps(spec.metadata, ensure_ascii=True),
                ),
            )
        return ScheduleRecord(
            schedule_id=schedule_id,
            owner_user_id=spec.owner_user_id,
            intent_text=spec.intent_text,
            run_at_utc=spec.run_at_utc,
            recurrence=spec.recurrence,
            metadata=spec.metadata,
        )

    def list_schedules(self) -> list[ScheduleRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM schedules ORDER BY run_at_utc ASC").fetchall()
        return [self._row_to_schedule(row) for row in rows]

    def delete_schedule(self, schedule_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM schedules WHERE schedule_id = ?", (schedule_id,))
            return cur.rowcount > 0

    def get_due_schedules(self, now: datetime) -> list[ScheduleRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM schedules WHERE run_at_utc <= ?", (now.isoformat(),)).fetchall()
        return [self._row_to_schedule(row) for row in rows]

    def upsert_skill(self, manifest: SkillManifest, enabled: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO skills_registry(name, enabled, manifest_json, updated_at_utc)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    enabled = excluded.enabled,
                    manifest_json = excluded.manifest_json,
                    updated_at_utc = excluded.updated_at_utc
                """,
                (
                    manifest.name,
                    int(enabled),
                    manifest.model_dump_json(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def list_skills(self) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT name, enabled, manifest_json FROM skills_registry ORDER BY name ASC").fetchall()
        return [
            {
                "name": row["name"],
                "enabled": bool(row["enabled"]),
                "manifest": json.loads(row["manifest_json"]),
            }
            for row in rows
        ]

    def set_skill_enabled(self, name: str, enabled: bool) -> bool:
        with self._connect() as conn:
            cur = conn.execute("UPDATE skills_registry SET enabled = ? WHERE name = ?", (int(enabled), name))
            return cur.rowcount > 0

    def get_skill(self, name: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT manifest_json FROM skills_registry WHERE name = ?", (name,)).fetchone()
        if row is None:
            return None
        return json.loads(row["manifest_json"])

    def add_security_audit_event(
        self,
        action: str,
        decision: str,
        metadata: dict[str, Any],
        created_at_utc: datetime | None = None,
    ) -> None:
        created = created_at_utc or datetime.now(timezone.utc)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO security_audit_events(created_at_utc, action, decision, metadata) VALUES (?, ?, ?, ?)",
                (created.isoformat(), action, decision, json.dumps(metadata, ensure_ascii=True)),
            )

    def list_security_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT created_at_utc, action, decision, metadata FROM security_audit_events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "created_at_utc": row["created_at_utc"],
                "action": row["action"],
                "decision": row["decision"],
                "metadata": json.loads(row["metadata"]),
            }
            for row in rows
        ]

    def _row_to_job(self, row: sqlite3.Row | dict[str, Any]) -> JobRecord:
        return JobRecord(
            job_id=row["job_id"],
            owner_user_id=row["owner_user_id"],
            source=JobSource(row["source"]),
            intent_text=row["intent_text"],
            plan_snapshot=json.loads(row["plan_snapshot"]),
            risk_level=RiskLevel(row["risk_level"]),
            status=JobStatus(row["status"]),
            run_at_utc=datetime.fromisoformat(row["run_at_utc"]),
            retry_count=int(row["retry_count"]),
            last_error=row["last_error"],
        )

    def _row_to_schedule(self, row: sqlite3.Row) -> ScheduleRecord:
        return ScheduleRecord(
            schedule_id=row["schedule_id"],
            owner_user_id=row["owner_user_id"],
            intent_text=row["intent_text"],
            run_at_utc=datetime.fromisoformat(row["run_at_utc"]),
            recurrence=row["recurrence"],
            metadata=json.loads(row["metadata"]),
        )

    def _row_to_approval(self, row: sqlite3.Row) -> ApprovalRecord:
        return ApprovalRecord(
            approval_id=row["approval_id"],
            job_id=row["job_id"],
            required_for_risk=RiskLevel(row["required_for_risk"]),
            prompt_summary=row["prompt_summary"],
            decision=ApprovalDecision(row["decision"]) if row["decision"] else None,
            decided_by=row["decided_by"],
            decided_at_utc=datetime.fromisoformat(row["decided_at_utc"]) if row["decided_at_utc"] else None,
        )
