from __future__ import annotations

import os
import time

from project_ash.autonomy.queue import JobQueue
from project_ash.autonomy.scheduler import Scheduler
from project_ash.config import load_default_config
from project_ash.memory.sqlite_store import SQLiteMemoryStore


def main() -> None:
    cfg = load_default_config()
    interval_seconds = float(os.getenv("ASH_SCHEDULER_POLL_SECONDS", "10"))

    store = SQLiteMemoryStore(cfg.sqlite_db_path)
    queue = JobQueue(store)
    scheduler = Scheduler(store, queue)

    while True:
        scheduler.dispatch_due_jobs()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
