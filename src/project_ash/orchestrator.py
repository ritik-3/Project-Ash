from __future__ import annotations

from pathlib import Path

from project_ash.executor import run_action
from project_ash.memory.sqlite_store import SQLiteMemoryStore, TaskLogRecord
from project_ash.models import ExecutionPlan, TaskResult, UserInput
from project_ash.nlu import parse_intent
from project_ash.planner import build_plan


class AssistantOrchestrator:
    def __init__(self, log_dir: Path, sqlite_db_path: Path | None = None) -> None:
        self.log_dir = log_dir
        self.sqlite_store = SQLiteMemoryStore(sqlite_db_path or (log_dir / "ash_memory.db"))

    def create_plan(self, user_input: UserInput) -> ExecutionPlan:
        parsed = parse_intent(user_input.text)
        return build_plan(user_input.text, parsed)

    def execute_plan(self, plan: ExecutionPlan) -> TaskResult:
        results = []
        all_success = True
        for step in plan.steps:
            result = run_action(step.step_id, step.action, step.params)
            results.append(result)
            if not result.success:
                all_success = False
                break

        summary = "Task completed." if all_success else "Task needs clarification or failed."
        self._log_execution(plan, summary, all_success)
        return TaskResult(success=all_success, summary=summary, step_results=results)

    def _log_execution(self, plan: ExecutionPlan, summary: str, success: bool) -> None:
        self.sqlite_store.add_task_log(
            TaskLogRecord(
                goal=plan.user_goal,
                summary=summary,
                success=success,
            )
        )
