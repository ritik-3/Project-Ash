from __future__ import annotations

import os
import time

from project_ash.autonomy.queue import JobQueue
from project_ash.autonomy.worker import Worker
from project_ash.config import load_default_config
from project_ash.orchestrator import AssistantOrchestrator


def main() -> None:
    cfg = load_default_config()
    interval_seconds = float(os.getenv("ASH_WORKER_POLL_SECONDS", "5"))

    orchestrator = AssistantOrchestrator(
        log_dir=cfg.log_dir,
        sqlite_db_path=cfg.sqlite_db_path,
        ollama_model=cfg.ollama_model,
    )
    store = orchestrator.sqlite_store
    queue = JobQueue(store)
    worker = Worker(orchestrator, store, queue)

    while True:
        worker.run_once()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
