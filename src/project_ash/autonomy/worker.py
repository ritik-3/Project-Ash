from __future__ import annotations

from project_ash.autonomy.queue import JobQueue
from project_ash.memory.sqlite_store import SQLiteMemoryStore
from project_ash.models import ApprovalDecision, InputMode, JobStatus, RiskLevel, UserInput
from project_ash.orchestrator import AssistantOrchestrator


class Worker:
    def __init__(self, orchestrator: AssistantOrchestrator, store: SQLiteMemoryStore, queue: JobQueue) -> None:
        self.orchestrator = orchestrator
        self.store = store
        self.queue = queue

    def run_once(self) -> bool:
        job = self.queue.next_job()
        if job is None:
            return False

        if job.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            approval = self.store.get_latest_approval(job.job_id)
            if approval is None:
                self.store.create_approval(
                    job_id=job.job_id,
                    required_for_risk=job.risk_level,
                    prompt_summary=f"Approval required for job '{job.intent_text}'",
                )
                self.store.update_job_status(job.job_id, JobStatus.WAITING_APPROVAL, last_error="Waiting for approval")
                return False

            if approval.decision == ApprovalDecision.DENIED:
                self.store.update_job_status(job.job_id, JobStatus.CANCELED, last_error="Approval denied")
                return False

            if approval.decision != ApprovalDecision.APPROVED:
                self.store.update_job_status(job.job_id, JobStatus.WAITING_APPROVAL, last_error="Waiting for approval")
                return False

        self.store.update_job_status(job.job_id, JobStatus.RUNNING)
        try:
            plan = self.orchestrator.create_plan(UserInput(mode=InputMode.TEXT, text=job.intent_text))
            result = self.orchestrator.execute_plan(plan, confirmed=True)
            status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
            self.store.update_job_status(job.job_id, status, last_error=None if result.success else result.summary)
            return result.success
        except Exception as exc:  # pragma: no cover
            self.store.update_job_status(job.job_id, JobStatus.FAILED, last_error=str(exc))
            return False
