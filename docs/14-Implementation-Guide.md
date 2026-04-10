# Implementation Guide

## Purpose
Describe how the current MVP foundation is implemented and how to extend it safely.

## Repository Structure
- `src/project_ash/models.py`: shared data models.
- `src/project_ash/nlu.py`: normalization and intent parsing.
- `src/project_ash/risk.py`: risk classification and confirmation policy.
- `src/project_ash/planner.py`: conversion from intent to execution plan.
- `src/project_ash/executor.py`: action dispatching.
- `src/project_ash/orchestrator.py`: plan+execute pipeline and logging.
- `src/project_ash/voice/`: STT and TTS adapters (baseline and local-stack adapters).
- `src/project_ash/llm/ollama_client.py`: local LLM integration adapter.
- `src/project_ash/automation/router.py`: deterministic action routing policy.
- `src/project_ash/api/server.py`: optional local FastAPI service layer.
- `src/project_ash/skills/`: desktop/browser/productivity/screen skills.
- `src/project_ash/memory/sqlite_store.py`: SQLite + FTS5 memory/log store.
- `tests/`: unit tests for parsing, planning, and risk.

## Runtime Flow
1. Input is captured from text or voice.
2. Voice input is transcribed to text.
3. NLU parses intent and entities.
4. Planner builds step-by-step plan with risk metadata.
5. Confirmation gate is applied for medium/high steps.
6. Executor runs each step through skill adapters.
7. Orchestrator writes task execution logs.
8. Final status is returned to user.

## Run Commands
- Install dependencies: `pip install -r requirements.txt`
- Install local-ai extras: `pip install -r requirements-local-ai.txt`
- Install automation extras: `pip install -r requirements-automation.txt`
- Install API extras: `pip install -r requirements-api.txt`
- Install package (editable): `pip install -e .`
- Start assistant: `python -m project_ash`
- Start local API server: `uvicorn project_ash.api.server:app --host 127.0.0.1 --port 8000`
- Run tests: `pytest`

## Extension Pattern
When adding a new capability:
1. Add intent detection in `nlu.py`.
2. Add risk mapping in `risk.py` if needed.
3. Add planner step mapping in `planner.py`.
4. Add skill function in `skills/`.
5. Add executor branch in `executor.py`.
6. Add unit and scenario tests.
7. Update capability and command docs.

## Safety Integration Rules
- Never bypass confirmation for medium/high risk actions.
- Keep irreversible actions blocked until explicit policy allows.
- Log every execution attempt with success/failure outcome.

## Known MVP Limits
- Screen summarization currently uses a safe placeholder.
- Voice mode is one-shot push-to-talk, not always-on wake mode.
- Productivity integrations are currently starter adapters and need app-specific connectors.
