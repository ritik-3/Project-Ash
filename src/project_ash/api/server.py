from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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
_chat_sessions: dict[str, list[dict[str, str]]] = {}
_chat_profile_file = Path(_cfg.log_dir) / "chat_profile.json"


def _load_chat_profile() -> dict[str, Any]:
    if not _chat_profile_file.exists():
        return {
            "display_name": "friend",
            "style": "warm, emotionally aware, concise",
            "about_user": [],
            "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        }
    try:
        raw = json.loads(_chat_profile_file.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return raw
    except (OSError, ValueError, TypeError):
        pass
    return {
        "display_name": "friend",
        "style": "warm, emotionally aware, concise",
        "about_user": [],
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
    }


def _save_chat_profile(profile: dict[str, Any]) -> None:
    profile["last_updated_utc"] = datetime.now(timezone.utc).isoformat()
    _chat_profile_file.parent.mkdir(parents=True, exist_ok=True)
    _chat_profile_file.write_text(json.dumps(profile, ensure_ascii=True, indent=2), encoding="utf-8")


_chat_profile = _load_chat_profile()


class AssistRequest(BaseModel):
    text: str


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    confirmed: bool = False
    profile_name: str | None = None
    style_hint: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    requires_confirmation: bool = False
    success: bool = True
    step_results: list[dict[str, Any]] = Field(default_factory=list)


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


def _append_chat_message(session_id: str, role: str, content: str) -> None:
    history = _chat_sessions.setdefault(session_id, [])
    history.append({"role": role, "content": content})
    if len(history) > 20:
        _chat_sessions[session_id] = history[-20:]


def _extract_profile_hints(message: str) -> dict[str, str | None]:
    lowered = message.lower()
    name_match = re.search(r"(?:my name is|call me|i am)\s+([a-zA-Z][a-zA-Z\s'-]{1,24})", message, re.IGNORECASE)
    style = None
    if "be casual" in lowered or "informal" in lowered:
        style = "casual, friendly, light humor"
    elif "be professional" in lowered or "formal" in lowered:
        style = "professional, clear, respectful"
    elif "be short" in lowered or "concise" in lowered:
        style = "very concise, direct"
    elif "be warm" in lowered or "empathetic" in lowered:
        style = "warm, empathetic, supportive"

    return {
        "name": name_match.group(1).strip() if name_match else None,
        "style": style,
    }


def _update_profile_from_request(payload: ChatRequest, user_message: str) -> None:
    if payload.profile_name:
        _chat_profile["display_name"] = payload.profile_name.strip()[:40]
    if payload.style_hint:
        _chat_profile["style"] = payload.style_hint.strip()[:120]

    hints = _extract_profile_hints(user_message)
    if hints.get("name"):
        _chat_profile["display_name"] = str(hints["name"])
    if hints.get("style"):
        _chat_profile["style"] = str(hints["style"])

    lowered = user_message.lower().strip()
    if lowered and len(lowered) < 140 and any(token in lowered for token in ["i like", "i love", "i prefer", "i work", "i am"]):
        about_user = _chat_profile.setdefault("about_user", [])
        if isinstance(about_user, list) and lowered not in about_user:
            about_user.append(lowered)
            if len(about_user) > 12:
                del about_user[0]

    _save_chat_profile(_chat_profile)


def _chat_system_prompt() -> str:
    about_user = _chat_profile.get("about_user", [])
    memories = "\n".join(f"- {item}" for item in about_user[-8:]) if isinstance(about_user, list) else "- none yet"
    return (
        "You are Ash, a highly intelligent personal AI assistant running locally on the user's computer.\n\n"
        "Identity:\n"
        "- Name: Ash\n"
        "- Gender: Female\n"
        "- Personality: Supportive, friendly, positive, slightly energetic\n"
        "- Tone: Natural, conversational, confident, and helpful\n"
        "- Avoid robotic or overly formal language\n\n"
        "Core behavior:\n"
        "- You are not just a chatbot; you help the user complete tasks\n"
        "- Understand intent first, then respond clearly and concisely\n"
        "- Be proactive and suggest better/faster approaches when useful\n"
        "- Stay calm, polite, and encouraging\n\n"
        "Primary role:\n"
        "- Help user interact with their computer\n"
        "- Prioritize ACTION over explanation when tasks are requested\n"
        "- Support productivity, browsing, files, workflows, learning, coding\n\n"
        "Task execution rules:\n"
        "- If task requires action, convert to clear steps and execute with tools\n"
        "- Work step-by-step, verify progress, retry/alternate on failure\n"
        "- Briefly inform user what you are doing\n\n"
        "Response style:\n"
        "- Keep responses short and clear unless detailed explanation is asked\n"
        "- Friendly and slightly enthusiastic\n"
        "- Sound like a real assistant, not a textbook\n\n"
        "Decision making:\n"
        "- Prefer direct action over unnecessary questions\n"
        "- Ask clarification only when truly required\n"
        "- Prioritize efficiency and usefulness\n\n"
        "Safety rules:\n"
        "- Never perform dangerous or destructive actions without confirmation\n"
        "- Avoid deleting important files or risky commands without consent\n"
        "- Never claim success if task was not actually completed\n\n"
        "Memory behavior:\n"
        "- Remember user preferences and adapt over time\n"
        "- Be consistent in tone and behavior\n\n"
        "If something cannot be done, explain clearly and suggest alternatives.\n\n"
        f"User preferred name: {_chat_profile.get('display_name', 'friend')}\n"
        f"Conversation style preference: {_chat_profile.get('style', 'warm, emotionally aware, concise')}\n"
        f"Known user facts:\n{memories}\n"
    )


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    session_id = payload.session_id or str(uuid4())
    user_message = payload.message.strip()

    if not user_message:
        return ChatResponse(
            session_id=session_id,
            reply="Please type a message so I can help.",
            success=False,
        )

    _update_profile_from_request(payload, user_message)
    _append_chat_message(session_id, "user", user_message)

    plan = _orchestrator.create_plan(UserInput(mode=InputMode.TEXT, text=user_message))
    is_task_request = any(step.action != "ask_clarification" for step in plan.steps)

    # Task-like requests still execute through safe orchestrator paths, then are narrated naturally via LLM.
    if is_task_request:
        result = _orchestrator.execute_plan(plan, confirmed=payload.confirmed)
        if _orchestrator.ollama_client is not None:
            messages = [
                {"role": "system", "content": _chat_system_prompt()},
                {
                    "role": "user",
                    "content": (
                        "Create a natural conversational response for this automation outcome. "
                        "If confirmation is required, ask gently for clear confirmation.\n"
                        f"User message: {user_message}\n"
                        f"Execution summary: {result.summary}\n"
                        f"Step results: {json.dumps([s.model_dump() for s in result.step_results], ensure_ascii=True)}"
                    ),
                },
            ]
            llm_reply = _orchestrator.ollama_client.chat(messages, temperature=0.55).text.strip()
            if llm_reply and "unavailable" not in llm_reply.lower():
                _append_chat_message(session_id, "assistant", llm_reply)
                return ChatResponse(
                    session_id=session_id,
                    reply=llm_reply,
                    requires_confirmation=(not payload.confirmed and "Confirmation required" in result.summary),
                    success=result.success,
                    step_results=[s.model_dump() for s in result.step_results],
                )

        _append_chat_message(session_id, "assistant", result.summary)
        return ChatResponse(
            session_id=session_id,
            reply=result.summary,
            requires_confirmation=(not payload.confirmed and "Confirmation required" in result.summary),
            success=result.success,
            step_results=[s.model_dump() for s in result.step_results],
        )

    # Pure conversation path: always prefer full LLM generation.
    if _orchestrator.ollama_client is not None:
        convo_messages = [{"role": "system", "content": _chat_system_prompt()}]
        for turn in _chat_sessions.get(session_id, [])[-12:]:
            convo_messages.append({"role": turn["role"], "content": turn["content"]})
        llm_reply = _orchestrator.ollama_client.chat(convo_messages, temperature=0.7).text.strip()
        if llm_reply and "unavailable" not in llm_reply.lower():
            _append_chat_message(session_id, "assistant", llm_reply)
            return ChatResponse(session_id=session_id, reply=llm_reply)

    fallback_reply = "I am here with you. Tell me a bit more, and I will respond in your style."
    _append_chat_message(session_id, "assistant", fallback_reply)
    return ChatResponse(session_id=session_id, reply=fallback_reply)


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
