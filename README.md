# Project Ash

Local-first desktop AI assistant with documentation-first planning and an implemented MVP foundation.

## Status

MVP foundation implemented (text + voice entry, intent parsing, risk-gated plan execution, and task logging).

Planning documentation is complete and connected to implementation artifacts.

## Implemented MVP Foundation

- Python package scaffold under `src/project_ash`.
- Text and push-to-talk voice input modes.
- Voice path uses faster-whisper primary STT with fallback.
- Natural language intent parsing for common daily commands.
- Ollama Llama 3.1-assisted planning/response path with rule-based fallback.
- Risk classification with confirmation gates.
- Planner, executor, and orchestrator pipeline.
- Routed execution adapters: Playwright (browser), UIA (desktop), OCR vision fallback.
- SQLite + FTS5 local task logs in `.project_ash/ash_memory.db`.
- Baseline unit tests in `tests`.

## Quick Start

1. Create and activate a Python virtual environment.
2. Install dependencies:
	- `pip install -r requirements.txt`
   - Optional local AI stack: `pip install -r requirements-local-ai.txt`
   - Optional automation stack: `pip install -r requirements-automation.txt`
   - Optional API-only stack (if you do not use the base requirements file): `pip install -r requirements-api.txt`
3. Configure runtime (voice enabled by default):
   - Edit `configs/app_config.json` if you want to set a Piper model path.
   - If Piper is not configured, speech output falls back to `pyttsx3`.
   - Playwright authenticated profile persists at `.project_ash/playwright-profile`.
4. Run assistant:
	- `python -m project_ash.cli`
   - First-run diagnostics: `python -m project_ash diagnostics`
5. Optional local API server:
   - `uvicorn project_ash.api.server:app --host 127.0.0.1 --port 8000`
   - Endpoints: `/health`, `/status`, `/diagnostics`, `/plan`, `/execute`, `/history`, `/assist`
6. Optional frontend app:
    - `cd frontend`
    - `npm install`
    - `npm run dev`
    - Open `http://127.0.0.1:5173`
   - Optional API override: set `VITE_API_BASE` (default is `http://127.0.0.1:8000`)
7. Choose mode:
	- `text` for chat-style control
	- `voice` for one-shot push-to-talk command
8. Confirm medium/high risk actions when prompted.

## Docker Quick Start

- Start local stack:
   - `docker compose up --build`
- Services:
   - API: `http://127.0.0.1:8000`
   - Frontend: `http://127.0.0.1:5173`
   - Ollama: `http://127.0.0.1:11434`

## Testing

- Run full test suite:
   - `pytest -q`
- Run diagnostics:
   - `python -m project_ash diagnostics`
- Build frontend (TypeScript + Vite):
   - `cd frontend && npm run build`
- Validate compose config:
   - `docker compose config`

## Current Verification Snapshot

- Full test suite: `32 passed`.
- Frontend production build: `passed`.
- Docker compose configuration: `validated`.

## Planning Documents

- [Idea](Idea.md)
- [Planning Charter](docs/00-Planning-Charter.md)
- [Product Requirements](docs/01-Product-Requirements.md)
- [System Architecture](docs/02-System-Architecture.md)
- [Roadmap And Milestones](docs/03-Roadmap-and-Milestones.md)
- [Documentation Checklist](docs/04-Documentation-Checklist.md)
- [Risks, Safety, And Privacy](docs/05-Risks-Safety-Privacy.md)
- [Architecture Decision Log](docs/06-Architecture-Decisions-Log.md)
- [Structured Review Status](docs/07-Structured-Review-Status.md)
- [Agent Capabilities And Task Catalog](docs/08-Agent-Capabilities-and-Task-Catalog.md)
- [Voice And Natural Language Design](docs/09-Voice-and-Natural-Language-Design.md)
- [Test Strategy](docs/10-Test-Strategy.md)
- [Rollout Plan](docs/11-Rollout-Plan.md)
- [Governance And Change Control](docs/12-Governance-and-Change-Control.md)
- [Top 50 Voice And Text Commands](docs/13-Top-50-Voice-Text-Commands.md)
- [Implementation Guide](docs/14-Implementation-Guide.md)
- [Target Tech Stack And Step-by-Step Execution Plan](docs/15-Target-Tech-Stack-and-Execution-Plan.md)
- [Full Stack Baseline (Frontend, Backend, Infra, Docker)](docs/16-Full-Stack-Baseline.md)
- [Agent Skills Setup (skills.sh)](docs/17-Agent-Skills-Setup.md)
- [Later Tasks](docs/18-Later-Tasks.md)

## Suggested Review Order

1. Idea
2. Planning Charter
3. Product Requirements
4. System Architecture
5. Risks, Safety, And Privacy
6. Roadmap And Milestones
7. Documentation Checklist
8. Architecture Decision Log
9. Structured Review Status
10. Agent Capabilities And Task Catalog
11. Voice And Natural Language Design
12. Test Strategy
13. Rollout Plan
14. Governance And Change Control
15. Top 50 Voice And Text Commands
16. Implementation Guide
17. Target Tech Stack And Step-by-Step Execution Plan
18. Full Stack Baseline
19. Agent Skills Setup
20. Later Tasks

## Approval Gate

Planning approval achieved and implementation started on 2026-04-11.