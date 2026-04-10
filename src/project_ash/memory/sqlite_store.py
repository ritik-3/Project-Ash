from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


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
