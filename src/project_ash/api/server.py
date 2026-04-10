from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from project_ash.config import load_default_config
from project_ash.models import InputMode, UserInput
from project_ash.orchestrator import AssistantOrchestrator

app = FastAPI(title="Project Ash Local API", version="0.1.0")
_cfg = load_default_config()
_orchestrator = AssistantOrchestrator(log_dir=_cfg.log_dir, sqlite_db_path=_cfg.sqlite_db_path)


class AssistRequest(BaseModel):
    text: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/assist")
def assist(payload: AssistRequest) -> dict:
    user_input = UserInput(mode=InputMode.TEXT, text=payload.text)
    plan = _orchestrator.create_plan(user_input)
    result = _orchestrator.execute_plan(plan)
    return {
        "summary": result.summary,
        "success": result.success,
        "steps": [s.model_dump() for s in result.step_results],
    }
