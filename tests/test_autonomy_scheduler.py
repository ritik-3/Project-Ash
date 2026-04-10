from datetime import datetime, timedelta, timezone

from project_ash.autonomy.models import ScheduleSpec
from project_ash.autonomy.queue import JobQueue
from project_ash.autonomy.scheduler import Scheduler
from project_ash.memory.sqlite_store import SQLiteMemoryStore


def test_scheduler_dispatches_due_jobs(tmp_path) -> None:
    store = SQLiteMemoryStore(tmp_path / "ash_memory.db")
    queue = JobQueue(store)
    scheduler = Scheduler(store, queue)

    spec = ScheduleSpec(
        owner_user_id="u1",
        intent_text="open github.com",
        run_at_utc=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    scheduler.create_schedule(spec)

    dispatched = scheduler.dispatch_due_jobs()
    assert dispatched == 1

    jobs = store.list_jobs()
    assert len(jobs) == 1
    assert jobs[0].intent_text == "open github.com"
