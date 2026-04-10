# Implementation Guide

## Purpose
Describe how the current MVP foundation is implemented and how to extend it safely.

## Repository Structure
- `src/project_ash/models.py`: shared data models.
- `src/project_ash/nlu.py`: normalization and intent parsing.
- `src/project_ash/nlu.py`: rule-based parsing plus Ollama-assisted intent parsing.
- `src/project_ash/risk.py`: risk classification and confirmation policy.
- `src/project_ash/planner.py`: conversion from intent to execution plan.
- `src/project_ash/executor.py`: action dispatching.
- `src/project_ash/orchestrator.py`: plan+execute pipeline and logging.
- `src/project_ash/voice/`: STT and TTS adapters (local primary with fallback).
- `src/project_ash/llm/ollama_client.py`: local LLM integration adapter.
- `src/project_ash/automation/router.py`: deterministic action routing policy.
- `src/project_ash/automation/browser_adapter.py`: Playwright browser workflows (web open/search, Gmail draft, Google Sheets actions).
- `src/project_ash/automation/desktop_adapter.py`: UIA desktop actions (app launch, active-window typing).
- `src/project_ash/automation/vision_adapter.py`: screenshot + OCR fallback with active window context.
- `src/project_ash/api/server.py`: optional local FastAPI service layer.
- `src/project_ash/diagnostics.py`: first-run environment and dependency diagnostics.
- `src/project_ash/skills/`: desktop/browser/productivity/screen skills.
- `src/project_ash/memory/sqlite_store.py`: SQLite + FTS5 memory/log store.
- `frontend/`: React + Vite frontend shell for API interaction.
- `tests/`: unit tests for parsing, planning, and risk.

## Runtime Flow
1. Input is captured from text or voice.
2. Voice input uses faster-whisper first, then falls back if needed.
3. NLU attempts Ollama-assisted intent parsing, then falls back to rule-based parsing.
4. Planner builds step-by-step plan with risk metadata.
5. Confirmation gate is applied for medium/high steps.
6. Executor routes actions: browser -> Playwright, desktop -> UIA, else vision fallback.
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
- API endpoints:
	- `GET /health`
	- `GET /status`
	- `POST /plan`
	- `POST /execute`
	- `POST /history`
	- `POST /assist`
	- `GET /diagnostics`
- Run tests: `pytest`

	## Playwright Persistent Auth Profile
	- Browser automation uses Playwright persistent context with user profile storage.
	- Profile directory comes from config: `playwright_user_data_dir`.
	- Default path: `.project_ash/playwright-profile`.
	- Log in once to Gmail/Sheets in this profile and future runs reuse that session.

## Voice Reply Setup (Current Machine)
- Piper executable installed in virtual environment: `c:/Ashu/Project-Ash/.venv/Scripts/piper.exe`.
- Voice model downloaded: `assets/voices/en_US-lessac-medium.onnx`.
- Runtime config enabled in `configs/app_config.json`.
- If Piper fails at runtime, assistant falls back to pyttsx3 automatically.

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
- Vision fallback quality depends on OCR package availability and page readability.
- Voice mode is one-shot push-to-talk, not always-on wake mode.
- Browser workflows that require authenticated sessions (Gmail/Sheets) depend on active user login state.
