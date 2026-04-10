from __future__ import annotations

from datetime import datetime, timezone

from project_ash.autonomy.models import ScheduleSpec
from project_ash.autonomy.queue import JobQueue
from project_ash.memory.sqlite_store import SQLiteMemoryStore
from project_ash.models import ScheduleRecord


class Scheduler:
    def __init__(self, store: SQLiteMemoryStore, queue: JobQueue) -> None:
        self.store = store
        self.queue = queue

    def create_schedule(self, spec: ScheduleSpec) -> ScheduleRecord:
        return self.store.create_schedule(spec)

    def list_schedules(self) -> list[ScheduleRecord]:
        return self.store.list_schedules()

    def delete_schedule(self, schedule_id: str) -> bool:
        return self.store.delete_schedule(schedule_id)

    def dispatch_due_jobs(self, now: datetime | None = None) -> int:
        run_now = now or datetime.now(timezone.utc)
        due = self.store.get_due_schedules(run_now)
        for sched in due:
            self.queue.enqueue(owner_user_id=sched.owner_user_id, intent_text=sched.intent_text, run_at_utc=run_now)
            if not sched.recurrence:
                self.store.delete_schedule(sched.schedule_id)
        return len(due)
