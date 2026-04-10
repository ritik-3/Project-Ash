# Full Stack Baseline (Frontend, Backend, Infra, Docker)

## Decision Scope
This document freezes the end-to-end technical stack for Project Ash local-first development and personal deployment.

## 1) Frontend Stack (Decided)
- Framework: React + Vite + TypeScript
- UI styling: Plain CSS (`frontend/src/styles.css`)
- State management: React local state/hooks
- API client: Native fetch
- API base URL: `VITE_API_BASE` env var (fallback `http://127.0.0.1:8000`)

Why this choice:
- Fast local development loop.
- Clean TypeScript integration.
- Easy migration to desktop shell (Tauri/Electron) later if required.

## 2) Backend Stack (Decided)
- Runtime: Python 3.10+
- API: FastAPI + Uvicorn
- Core logic: Project Ash orchestrator modules
- Validation: Pydantic

Why this choice:
- Already aligned with current codebase.
- Strong typing and clean API patterns.

## 3) AI/Voice Stack (Decided)
- Local LLM runtime: Ollama
- Primary model family: Llama 3.1 (quantized for local GPU)
- STT: faster-whisper (CUDA)
- TTS: Piper
- Wake-word (later phase): openWakeWord (Porcupine optional)

## 4) Automation Stack (Decided)
- Browser automation: Playwright
- Desktop automation: pywinauto + Windows UI Automation
- Vision fallback: mss + OCR (EasyOCR baseline)

Deterministic route policy:
1. If browser target detected -> Playwright
2. Else if desktop target detected -> OS automation
3. Else -> screenshot + OCR fallback

## 5) Memory And Data Stack (Decided)
- Primary store: SQLite + FTS5
- Data domains:
  - Task logs
  - Preferences
  - Session context snapshots
- Vector DB: deferred until semantic memory workloads justify it

## 6) Infra Stack (Decided)
- Environment: Local-first on Windows workstation
- Container runtime: Docker Desktop
- GPU path for LLM containers: NVIDIA-enabled Docker setup
- Service communication: localhost network only by default

## 7) Docker Strategy (Decided)
- Compose-based local orchestration:
  - `ash-api` (FastAPI)
  - `ash-worker` (autonomy worker loop)
  - `ash-scheduler` (autonomy scheduler loop)
  - `ollama` (local model runtime)
  - `ash-frontend` (React app served via nginx)
- Persistent volumes:
  - SQLite/database files
  - Ollama model cache

## 8) CI/CD Baseline (Decided)
- Source control: GitHub
- CI: GitHub Actions
- Initial CI pipeline:
  - Python setup
  - Dependency install
  - Test execution via `pytest -q`
  - Lint/static checks (deferred)

## 8.1) Agent Skills Baseline (Decided)
- Skills manager: skills.sh CLI via npx skills
- Installed project skills:
  - fastapi-templates
  - playwright-best-practices
  - docker-expert
  - typescript-react-reviewer
- Project-specific skill scaffold: project-ash-skill-kit/SKILL.md

## 9) Security Baseline (Decided)
- Local-first and no cloud fallback by default.
- Secrets via environment variables, never hardcoded.
- Confirmation gate for medium/high risk operations.
- Audit logs for executed tasks.

## 10) Deployment Modes
- Mode A (Current): Local CLI usage.
- Mode B: Local API service + frontend UI.
- Mode C (Later): Desktop packaged app shell.

## 11) What Is Deferred
- Kubernetes or distributed deployment.
- Multi-user auth and tenant isolation.
- Production cloud environment.

## 12) Immediate Build Order
1. Keep backend and API stable.
2. Maintain frontend integration with `/execute` and `/status`.
3. Keep Docker local compose workflow healthy (`docker compose config` + full stack up).
4. Keep Playwright/desktop adapters stable under route policy.
5. Continue hardening observability and safety regression tests.

## 13) Readiness Snapshot (2026-04-11)
- API CORS for frontend local origins is enabled.
- Frontend response contract is aligned with backend task result payload.
- Frontend TypeScript build baseline is valid (Vite ambient typing in place).
- Full backend test suite status: `32 passed`.
- Frontend production build status: `passed`.
