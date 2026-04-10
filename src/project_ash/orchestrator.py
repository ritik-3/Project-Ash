from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_ash.autonomy.queue import JobQueue
from project_ash.executor import run_action
from project_ash.llm.ollama_client import OllamaClient
from project_ash.memory.sqlite_store import SQLiteMemoryStore, TaskLogRecord
from project_ash.models import ChannelEnvelope, ExecutionPlan, InputMode, JobSource, PlanStep, RiskLevel, StepResult, TaskResult, UserInput
from project_ash.nlu import parse_intent, parse_intent_with_ollama
from project_ash.planner import build_plan
from project_ash.security.audit import AuditLogger
from project_ash.security.injection_guard import InjectionGuard
from project_ash.security.sanitizer import sanitize_text
from project_ash.skills.policy import PolicyGuard


class AssistantOrchestrator:
    def __init__(self, log_dir: Path, sqlite_db_path: Path | None = None, ollama_model: str | None = None) -> None:
        self.log_dir = log_dir
        self.sqlite_store = SQLiteMemoryStore(sqlite_db_path or (log_dir / "ash_memory.db"))
        self.ollama_client = OllamaClient(model=ollama_model) if ollama_model else None
        self.policy_guard = PolicyGuard()
        self.injection_guard = InjectionGuard()
        self.audit_logger = AuditLogger(self.sqlite_store)
        self.job_queue = JobQueue(self.sqlite_store)
        self.current_state: dict[str, Any] = {
            "phase": "idle",
            "last_goal": None,
            "last_success": None,
            "last_summary": None,
        }

    def create_plan(self, user_input: UserInput) -> ExecutionPlan:
        user_input = UserInput(mode=user_input.mode, text=sanitize_text(user_input.text))
        if self.injection_guard.is_suspicious(user_input.text):
            self.audit_logger.log("input_prefilter", "blocked", {"reason": "possible_prompt_injection"})
            return ExecutionPlan(
                user_goal=user_input.text,
                steps=[
                    PlanStep(
                        step_id=0,
                        action="ask_clarification",
                        params={"question": "Request blocked by safety prefilter."},
                        risk=RiskLevel.LOW,
                        requires_confirmation=False,
                        execution_mode="immediate",
                        tags=["blocked", "injection"],
                    )
                ],
            )

        self.current_state["phase"] = "planning"
        self.current_state["last_goal"] = user_input.text
        parsed = None
        if self.ollama_client is not None:
            parsed = parse_intent_with_ollama(user_input.text, self.ollama_client)
        if parsed is None:
            parsed = parse_intent(user_input.text)
        plan = build_plan(user_input.text, parsed)
        self.current_state["phase"] = "planned"
        return plan

    def execute_plan(self, plan: ExecutionPlan, confirmed: bool = False) -> TaskResult:
        self.current_state["phase"] = "executing"
        self.current_state["last_goal"] = plan.user_goal
        if not plan.steps:
            return TaskResult(success=False, summary="No plan steps available.", step_results=[])

        if any(getattr(step, "execution_mode", "immediate") == "async" for step in plan.steps):
            queued = self.sqlite_store.create_job(
                owner_user_id="local-user",
                source=JobSource.SCHEDULED,
                intent_text=plan.user_goal,
                plan_snapshot=plan.model_dump(),
                risk_level=max((step.risk for step in plan.steps), key=lambda r: [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH].index(r)),
                run_at_utc=datetime.now(timezone.utc),
            )
            summary = f"Task queued as job {queued.job_id}."
            self._log_execution(plan, summary, True)
            self.audit_logger.log("job_enqueue", "allowed", {"job_id": queued.job_id})
            return TaskResult(success=True, summary=summary, step_results=[])

        if any(step.requires_confirmation for step in plan.steps) and not confirmed:
            result = TaskResult(
                success=False,
                summary="Confirmation required before executing medium/high risk actions.",
                step_results=[
                    StepResult(
                        step_id=0,
                        success=False,
                        message="Execution blocked by confirmation gate.",
                    )
                ],
            )
            self._log_execution(plan, result.summary, False)
            self.current_state.update(
                {
                    "phase": "blocked_confirmation",
                    "last_success": False,
                    "last_summary": result.summary,
                }
            )
            return result

        results = []
        all_success = True
        for step in plan.steps:
            result = run_action(step.step_id, step.action, step.params, step=step, policy_guard=self.policy_guard)
            results.append(result)
            if not result.success:
                self.audit_logger.log("policy_or_execution", "blocked", {"step_id": step.step_id, "action": step.action})
                all_success = False
                break

        summary = self._summarize_task_result(plan, results, all_success)
        self._log_execution(plan, summary, all_success)
        self.current_state.update(
            {
                "phase": "idle",
                "last_success": all_success,
                "last_summary": summary,
            }
        )
        return TaskResult(success=all_success, summary=summary, step_results=results)

    def handle_channel_envelope(self, envelope: ChannelEnvelope) -> TaskResult:
        plan = self.create_plan(UserInput(mode=InputMode.TEXT, text=envelope.message_text))
        return self.execute_plan(plan, confirmed=False)

    def get_history(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        rows = self.sqlite_store.search_task_logs(query=query, limit=limit)
        return [dict(row) for row in rows]

    def get_runtime_status(self) -> dict[str, Any]:
        return dict(self.current_state)

    def _summarize_task_result(self, plan: ExecutionPlan, results: list[StepResult], success: bool) -> str:
        if self.ollama_client is None:
            return "Task completed." if success else "Task needs clarification or failed."

        payload = {
            "goal": plan.user_goal,
            "success": success,
            "steps": [r.model_dump() for r in results],
        }
        prompt = (
            "Summarize this automation result in one concise sentence for the user. "
            "Include whether it completed successfully. Data: "
            f"{json.dumps(payload)}"
        )
        llm_response = self.ollama_client.generate(prompt, temperature=0.1).text.strip()
        if llm_response and "unavailable" not in llm_response.lower():
            return llm_response
        return "Task completed." if success else "Task needs clarification or failed."

    def _log_execution(self, plan: ExecutionPlan, summary: str, success: bool) -> None:
        self.sqlite_store.add_task_log(
            TaskLogRecord(
                goal=plan.user_goal,
                summary=summary,
                success=success,
            )
        )
