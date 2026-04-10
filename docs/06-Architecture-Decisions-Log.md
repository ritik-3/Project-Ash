# Architecture Decision Log (ADL)

This file tracks frozen planning decisions for Project Ash before implementation.

## ADL-001: Model Strategy
- Date: 2026-04-10
- Status: Accepted
- Context: Need privacy-first operation with practical quality.
- Options considered:
  - Fully local only
  - Fully cloud only
  - Local-first hybrid
- Decision: Local-first hybrid.
- Details:
  - Default: local model for planning and assistant responses.
  - Optional cloud fallback: disabled by default and requires explicit opt-in.
- Consequences:
  - Better privacy baseline.
  - Better resilience when local model quality is insufficient.

## ADL-002: Execution Determinism
- Date: 2026-04-10
- Status: Accepted
- Context: Need reliable action execution.
- Options considered:
  - Model controls both planning and execution directly
  - Deterministic planner only
  - Model planning plus deterministic execution
- Decision: Model planning plus deterministic execution.
- Details:
  - Model creates/updates plan.
  - Executor runs only validated skill calls with schema checks.
- Consequences:
  - Improved reliability and safety.
  - Additional engineering effort for validators.

## ADL-003: Runtime Stack
- Date: 2026-04-10
- Status: Accepted
- Context: Need a practical local stack for Windows desktop automation.
- Options considered:
  - Python-centric stack
  - TypeScript-centric stack
  - Polyglot service split
- Decision: Python-centric stack for MVP.
- Details:
  - Python for orchestration, policy checks, and automation adapters.
- Consequences:
  - Faster MVP setup for automation-heavy workflows.
  - Frontend can remain decoupled for future changes.

## ADL-004: Browser Automation Depth (MVP)
- Date: 2026-04-10
- Status: Accepted
- Context: Browser workflows are valuable but risky.
- Options considered:
  - Deep unrestricted web automation
  - Limited allowlisted automation
  - Manual-only assist mode
- Decision: Limited allowlisted automation.
- Details:
  - MVP supports predefined workflow templates on approved domains.
  - Irreversible submits always require explicit confirmation.
- Consequences:
  - Lower risk and higher stability.
  - Reduced flexibility in early versions.

## ADL-005: Memory And Storage Format
- Date: 2026-04-10
- Status: Accepted
- Context: Need local persistence for logs and lightweight memory.
- Options considered:
  - Flat files
  - SQLite
  - External vector database
- Decision: SQLite-backed local storage for MVP.
- Details:
  - Use structured tables for tasks, action logs, and preference memory.
  - Add lightweight indexing for retrieval.
- Consequences:
  - Simple local deployment.
  - Future migration may be needed for large-scale indexing.

## ADL-006: Data Retention Policy (MVP)
- Date: 2026-04-10
- Status: Accepted
- Context: Need privacy-aware memory lifecycle.
- Options considered:
  - Keep all data indefinitely
  - Strictly ephemeral only
  - Tiered retention
- Decision: Tiered retention.
- Details:
  - Session context: clears at session end unless saved.
  - Action logs: retain 30 days by default.
  - Preferences: retained until user deletes.
- Consequences:
  - Better privacy control.
  - Requires user-visible retention settings.

## ADL-007: Permission Model Granularity
- Date: 2026-04-10
- Status: Accepted
- Context: Need clear trust boundaries.
- Options considered:
  - Binary allow/deny
  - Three-tier risk model
  - Per-command custom policy only
- Decision: Three-tier risk model with policy overlays.
- Details:
  - Low: auto-execute.
  - Medium: single confirmation.
  - High: strict confirmation and policy guardrails.
- Consequences:
  - Clear UX and safer defaults.
  - Needs reliable risk classification.

## ADL-008: Packaging And Deployment (MVP)
- Date: 2026-04-10
- Status: Accepted
- Context: Need local personal deployment without heavy infrastructure.
- Options considered:
  - Source-only scripts
  - Local desktop package
  - Distributed microservices
- Decision: Local single-machine package for personal use.
- Details:
  - One-machine runtime with local config and storage.
- Consequences:
  - Easy personal operation.
  - Multi-user scaling is deferred.

## ADL-009: Local LLM Provider And Model
- Date: 2026-04-11
- Status: Accepted
- Context: Need local, practical inference quality on RTX 3060 12GB.
- Options considered:
  - llama.cpp direct only
  - Ollama model runtime
  - Cloud-only API models
- Decision: Ollama with Llama 3.1 instruction model as primary.
- Details:
  - Default target model family: Llama 3.1.
  - Use quantized variants that fit local GPU memory.
- Consequences:
  - Local privacy-first behavior.
  - Easy model management and upgrades.

## ADL-010: Local Voice Stack
- Date: 2026-04-11
- Status: Accepted
- Context: Need fully local voice processing.
- Options considered:
  - Cloud STT + local TTS
  - Fully local STT/TTS
- Decision: faster-whisper (CUDA) for STT and Piper for TTS.
- Details:
  - STT: faster-whisper on GPU for near real-time transcription.
  - TTS: Piper as preferred local voice synthesizer.
  - Existing libraries may remain as fallback during migration.
- Consequences:
  - Better privacy and lower ongoing cloud dependency.
  - Requires model/voice asset management.

## ADL-011: Wake Word Strategy
- Date: 2026-04-11
- Status: Accepted
- Context: Need optional always-listening mode in later phase.
- Options considered:
  - No wake word
  - openWakeWord
  - Porcupine
- Decision: openWakeWord primary (Porcupine optional alternative).
- Details:
  - Keep wake-word disabled by default in MVP.
  - Enable in later phase behind explicit setting.
- Consequences:
  - Better hands-free UX in later versions.
  - Additional false-trigger tuning required.

## ADL-012: Automation Routing Policy
- Date: 2026-04-11
- Status: Accepted
- Context: Need deterministic action routing.
- Decision: Apply strict route selection rule.
- Rule:
  - If browser task, use Playwright DOM control.
  - Else if desktop-app task, use OS automation (pywinauto/UIA).
  - Else use screenshot vision fallback.
- Consequences:
  - Predictable behavior and easier debugging.
  - Vision fallback must be robustly validated.

## ADL-013: Memory Storage Baseline
- Date: 2026-04-11
- Status: Accepted
- Context: Need searchable local logs and preferences.
- Decision: SQLite with FTS5 for logs and memory.
- Consequences:
  - Fast local retrieval.
  - Structured migrations needed over time.

## ADL-014: Local Service Layer
- Date: 2026-04-11
- Status: Accepted
- Context: Need clean separation between UI and assistant runtime.
- Decision: FastAPI local server as optional service layer.
- Consequences:
  - Cleaner client separation and future extensibility.
  - Adds service lifecycle management overhead.

## ADL-015: Frontend Technology Baseline
- Date: 2026-04-11
- Status: Accepted
- Context: Need a lightweight local UI stack compatible with API-first architecture.
- Decision: React + Vite + TypeScript with Tailwind CSS and Zustand.
- Consequences:
  - Fast local development and UI iteration.
  - Requires frontend project bootstrap in next implementation phase.

## ADL-016: Docker And Local Infra Baseline
- Date: 2026-04-11
- Status: Accepted
- Context: Need reproducible local environment across services.
- Decision: Docker Desktop + Compose for API and Ollama services.
- Consequences:
  - Standardized local startup.
  - GPU acceleration setup must be validated per machine.

## ADL-017: CI Baseline
- Date: 2026-04-11
- Status: Accepted
- Context: Need automated validation for each push and PR.
- Decision: GitHub Actions CI with dependency install and pytest run.
- Consequences:
  - Fast feedback cycle.
  - Lint/type gates should be added in next iteration.
