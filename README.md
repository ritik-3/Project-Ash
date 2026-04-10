# Project Ash

Local-first desktop AI assistant with documentation-first planning and an implemented MVP foundation.

## Status

MVP foundation implemented (text + voice entry, intent parsing, risk-gated plan execution, and task logging).

Planning documentation is complete and connected to implementation artifacts.

## Implemented MVP Foundation

- Python package scaffold under `src/project_ash`.
- Text and push-to-talk voice input modes.
- Natural language intent parsing for common daily commands.
- Risk classification with confirmation gates.
- Planner, executor, and orchestrator pipeline.
- Basic desktop/browser/productivity skill adapters.
- SQLite + FTS5 local task logs in `.project_ash/ash_memory.db`.
- Baseline unit tests in `tests`.

## Quick Start

1. Create and activate a Python virtual environment.
2. Install dependencies:
	- `pip install -r requirements.txt`
   - Optional local AI stack: `pip install -r requirements-local-ai.txt`
   - Optional automation stack: `pip install -r requirements-automation.txt`
   - Optional API stack: `pip install -r requirements-api.txt`
3. Run assistant:
	- `python -m project_ash.cli`
4. Optional local API server:
   - `uvicorn project_ash.api.server:app --host 127.0.0.1 --port 8000`
5. Choose mode:
	- `text` for chat-style control
	- `voice` for one-shot push-to-talk command
6. Confirm medium/high risk actions when prompted.

## Testing

- Run unit tests:
  - `pytest`

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

## Approval Gate

Planning approval achieved and implementation started on 2026-04-11.