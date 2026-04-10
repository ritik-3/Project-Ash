from pathlib import Path

from project_ash.memory.sqlite_store import SQLiteMemoryStore, TaskLogRecord


def test_sqlite_store_add_and_search(tmp_path: Path) -> None:
    db_path = tmp_path / "ash_memory.db"
    store = SQLiteMemoryStore(db_path)

    store.add_task_log(TaskLogRecord(goal="open chrome", summary="Task completed.", success=True))
    rows = store.search_task_logs("chrome")

    assert len(rows) >= 1
    assert rows[0]["goal"] == "open chrome"
