from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from project_ash.autonomy.models import ScheduleSpec
from project_ash.autonomy.queue import JobQueue
from project_ash.autonomy.scheduler import Scheduler
from project_ash.autonomy.worker import Worker
from project_ash.channels.router import ChannelRouter
from project_ash.config import load_default_config
from project_ash.diagnostics import run_diagnostics
from project_ash.models import ApprovalDecision, ExecutionPlan, InputMode, JobSource, JobStatus, RiskLevel, UserInput
from project_ash.orchestrator import AssistantOrchestrator
from project_ash.skills.registry import SkillRegistry

app = FastAPI(title="Project Ash Local API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_cfg = load_default_config()
_orchestrator = AssistantOrchestrator(
    log_dir=_cfg.log_dir,
    sqlite_db_path=_cfg.sqlite_db_path,
    ollama_model=_cfg.ollama_model,
)
_store = _orchestrator.sqlite_store
_channels = ChannelRouter()
_queue = JobQueue(_store)
_scheduler = Scheduler(_store, _queue)
_worker = Worker(_orchestrator, _store, _queue)
_skill_registry = SkillRegistry(_store)


class AssistRequest(BaseModel):
    text: str


class PlanRequest(BaseModel):
    text: str
    mode: InputMode = InputMode.TEXT


class ExecuteRequest(BaseModel):
    text: str | None = None
    plan: dict[str, Any] | None = None
    confirmed: bool = False


class HistoryQuery(BaseModel):
    query: str
    limit: int = 10


class ChannelSendRequest(BaseModel):
    provider: str
    channel_conversation_id: str
    text: str


class JobCreateRequest(BaseModel):
    owner_user_id: str = "local-user"
    intent_text: str
    run_at_utc: datetime | None = None


class ScheduleCreateRequest(BaseModel):
    owner_user_id: str = "local-user"
    intent_text: str
    run_at_utc: datetime
    recurrence: str | None = None


class SkillInstallRequest(BaseModel):
    manifest_path: str


class ApprovalDecisionRequest(BaseModel):
    decided_by: str = "local-user"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/channels/health")
def channels_health() -> dict[str, Any]:
    return {"status": "ok", "providers": _cfg.channel_providers_enabled}


@app.get("/status")
def status() -> dict[str, Any]:
    runtime = _orchestrator.get_runtime_status()
    return {
        "status": "ready",
        "model": _cfg.ollama_model,
        "sqlite_db": str(_cfg.sqlite_db_path),
        "runtime": runtime,
    }


@app.get("/diagnostics")
def diagnostics() -> dict[str, Any]:
    report = run_diagnostics(_cfg)
    return {
        "results": [r.__dict__ for r in report],
        "ok": not any(r.status == "fail" for r in report),
    }


@app.post("/plan")
def plan(payload: PlanRequest) -> dict[str, Any]:
    user_input = UserInput(mode=payload.mode, text=payload.text)
    execution_plan = _orchestrator.create_plan(user_input)
    return execution_plan.model_dump()


@app.post("/execute")
def execute(payload: ExecuteRequest) -> dict[str, Any]:
    if payload.plan is None and payload.text is None:
        raise HTTPException(status_code=400, detail="Provide either text or plan.")

    if payload.plan is not None:
        execution_plan = ExecutionPlan.model_validate(payload.plan)
    else:
        user_input = UserInput(mode=InputMode.TEXT, text=payload.text or "")
        execution_plan = _orchestrator.create_plan(user_input)

    result = _orchestrator.execute_plan(execution_plan, confirmed=payload.confirmed)
    return result.model_dump()


@app.post("/history")
def history(payload: HistoryQuery) -> dict[str, Any]:
    items = _orchestrator.get_history(payload.query, limit=payload.limit)
    return {"items": items}


@app.post("/assist")
def assist(payload: AssistRequest) -> dict:
    user_input = UserInput(mode=InputMode.TEXT, text=payload.text)
    plan = _orchestrator.create_plan(user_input)
    result = _orchestrator.execute_plan(plan, confirmed=False)
    return {
        "summary": result.summary,
        "success": result.success,
        "steps": [s.model_dump() for s in result.step_results],
    }


@app.post("/channels/webhook/{provider}")
def channel_webhook(provider: str, payload: dict[str, Any]) -> dict[str, Any]:
    if provider not in _cfg.channel_providers_enabled:
        raise HTTPException(status_code=403, detail="Channel provider disabled")

    envelope = _channels.normalize(provider, payload)
    result = _orchestrator.handle_channel_envelope(envelope)
    return {
        "envelope_id": envelope.envelope_id,
        "provider": provider,
        "success": result.success,
        "summary": result.summary,
    }


@app.post("/channels/send")
def channels_send(payload: ChannelSendRequest) -> dict[str, Any]:
    outbound = _channels.prepare_outbound(payload.provider, payload.channel_conversation_id, payload.text)
    return {"provider": payload.provider, "payload": outbound, "status": "queued_for_provider"}


@app.post("/jobs")
def create_job(payload: JobCreateRequest) -> dict[str, Any]:
    job = _store.create_job(
        owner_user_id=payload.owner_user_id,
        source=JobSource.SCHEDULED,
        intent_text=payload.intent_text,
        plan_snapshot={},
        risk_level=RiskLevel.MEDIUM,
        run_at_utc=payload.run_at_utc or datetime.now(timezone.utc),
    )
    return job.model_dump()


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    job = _store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.model_dump()


@app.get("/jobs")
def list_jobs(limit: int = 100) -> dict[str, Any]:
    return {"items": [job.model_dump() for job in _store.list_jobs(limit=limit)]}


@app.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict[str, Any]:
    ok = _store.update_job_status(job_id, JobStatus.CANCELED)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": JobStatus.CANCELED.value}


@app.post("/jobs/{job_id}/retry")
def retry_job(job_id: str) -> dict[str, Any]:
    ok = _store.increment_job_retry(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": JobStatus.QUEUED.value}


@app.post("/jobs/run-once")
def run_job_worker_once() -> dict[str, Any]:
    executed = _worker.run_once()
    return {"executed": executed}


@app.post("/schedules")
def create_schedule(payload: ScheduleCreateRequest) -> dict[str, Any]:
    spec = ScheduleSpec(
        owner_user_id=payload.owner_user_id,
        intent_text=payload.intent_text,
        run_at_utc=payload.run_at_utc,
        recurrence=payload.recurrence,
    )
    schedule = _scheduler.create_schedule(spec)
    return schedule.model_dump()


@app.get("/schedules")
def list_schedules() -> dict[str, Any]:
    return {"items": [item.model_dump() for item in _scheduler.list_schedules()]}


@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: str) -> dict[str, Any]:
    ok = _scheduler.delete_schedule(schedule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"deleted": True}


@app.post("/skills/install")
def install_skill(payload: SkillInstallRequest) -> dict[str, Any]:
    manifest = _skill_registry.install_from_file(Path(payload.manifest_path))
    return manifest.model_dump()


@app.get("/skills")
def list_skills() -> dict[str, Any]:
    return {"items": _skill_registry.list_skills()}


@app.post("/skills/{skill_name}/enable")
def enable_skill(skill_name: str) -> dict[str, Any]:
    ok = _skill_registry.set_enabled(skill_name, True)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"skill_name": skill_name, "enabled": True}


@app.post("/skills/{skill_name}/disable")
def disable_skill(skill_name: str) -> dict[str, Any]:
    ok = _skill_registry.set_enabled(skill_name, False)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"skill_name": skill_name, "enabled": False}


@app.get("/skills/{skill_name}/manifest")
def skill_manifest(skill_name: str) -> dict[str, Any]:
    manifest = _skill_registry.get_manifest(skill_name)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return manifest.model_dump()


@app.post("/approvals/{job_id}/approve")
def approve_job(job_id: str, payload: ApprovalDecisionRequest) -> dict[str, Any]:
    ok = _store.set_approval_decision(job_id, ApprovalDecision.APPROVED, payload.decided_by)
    if not ok:
        raise HTTPException(status_code=404, detail="Pending approval not found")
    _store.update_job_status(job_id, JobStatus.QUEUED, last_error=None)
    return {"job_id": job_id, "decision": ApprovalDecision.APPROVED.value}


@app.post("/approvals/{job_id}/deny")
def deny_job(job_id: str, payload: ApprovalDecisionRequest) -> dict[str, Any]:
    ok = _store.set_approval_decision(job_id, ApprovalDecision.DENIED, payload.decided_by)
    if not ok:
        raise HTTPException(status_code=404, detail="Pending approval not found")
    _store.update_job_status(job_id, JobStatus.CANCELED, last_error="Approval denied")
    return {"job_id": job_id, "decision": ApprovalDecision.DENIED.value}


@app.get("/approvals/pending")
def pending_approvals() -> dict[str, Any]:
    return {"items": [item.model_dump() for item in _store.list_pending_approvals()]}
