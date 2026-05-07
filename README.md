# Ash Assistant

Ash Assistant is a hybrid, local-first desktop AI assistant project built around a FastAPI backend, modular providers, and a safety-first orchestration layer.

The repo is currently focused on the `assistant-api` service, with the full intended architecture documented under `docs/`.

## What This Project Covers

- Voice and chat interactions
- Local LLM integration with cloud fallback
- Desktop and browser automation
- Memory, orchestration, and policy checks
- Logging, retries, and recoverability

## Repository Layout

- `apps/assistant-api` - FastAPI backend scaffold for the assistant service
- `docs/` - product vision, system specs, and planned structure
- `guide/` - implementation notes and phased rollout guidance
- `requirements.txt` - Python dependencies for the current backend scaffold

## Quick Start

```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
.\scripts\start_local.ps1
```

The service exposes a health check at `/api/v1/health`.

## Development Notes

- The project targets a Windows desktop workflow.
- The backend uses FastAPI, Pydantic, SQLAlchemy, Tenacity, Loguru, and several local assistant integrations.
- Some capabilities are planned in the docs but not yet implemented in the current scaffold.

## Documentation

- [Project Structure](docs/Project-Structure.md)
- [System Specs](docs/System-Specs.md)
- [Idea](docs/Idea.md)
- [assistant-api README](apps/assistant-api/README.md)

## GitHub And CI

- `.github/workflows/ci.yml` runs a lightweight validation job that compiles the backend sources on push and pull request.
- `.gitignore` excludes virtual environments, caches, logs, local databases, and runtime artifacts.

## Next Steps

1. Flesh out the remaining API endpoints and service layers described in the docs.
2. Add tests for orchestration, memory, and health endpoints.
3. Expand CI once the dependency set is stable enough for install-and-test validation.
