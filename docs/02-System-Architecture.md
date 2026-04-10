# System Architecture (Frozen MVP Baseline)

## 1. Architecture Goals
- Local-first execution for privacy and speed.
- Controlled autonomy with explicit permission boundaries.
- Modular components with clean interfaces.
- Observability and reproducibility of actions.

## 2. High-Level Component Model
- Interface Layer
- Speech Processing Layer
- Orchestration Layer
- Skill Execution Layer
- Memory Layer
- Safety and Policy Layer
- Logging and Telemetry Layer

## 3. Component Responsibilities

### Interface Layer
- Accept text commands and push-to-talk voice commands.
- Display assistant reasoning summary, step plan, and progress.
- Capture approvals for sensitive actions.

### Speech Processing Layer
- Convert voice input to text with confidence scoring.
- Normalize casual and mixed-language phrasing before intent parsing.
- Convert final responses to optional speech output.

### Orchestration Layer
- Convert user intent into executable plan.
- Select tools/skills per task step.
- Manage retries, fallback logic, and clarifications.

### Skill Execution Layer
- Desktop Control Skill: app launch, file navigation, basic system actions.
- Browser Skill: open sites, guided interactions, information capture.
- Productivity Skill: reminders, structured notes, repeat workflows.

### Memory Layer
- Session memory: current task context.
- Profile memory: user preferences and frequently used commands.
- Knowledge memory: reusable task templates.

### Safety and Policy Layer
- Risk score each action.
- Enforce confirmation for risky operations.
- Block forbidden operations by policy.

### Logging and Telemetry Layer
- Record intent, selected plan, actions taken, and results.
- Support debugging and reliability analysis.

## 4. Data Flow
1. User submits text or voice instruction.
2. If voice is used, speech layer transcribes and confidence-scores input.
3. Intent parser normalizes instruction and extracts constraints.
4. Orchestrator builds step plan.
5. Safety layer evaluates each step risk.
6. Approved steps execute via skills.
7. Results stream back to UI with logs and optional speech response.
8. Memory updates with relevant context.

## 5. Integration Boundaries
- Internal APIs between orchestrator and skills should be schema-defined.
- Skill contracts should include: input schema, output schema, risk level, retry strategy.
- Memory access should be permission-aware.

## 6. Technology Direction (Frozen For MVP)
- Language/runtime: Python-centric orchestration stack.
- Frontend baseline: React + Vite + TypeScript + Tailwind CSS + Zustand.
- Desktop automation: pywinauto + UI Automation.
- Browser automation: Playwright DOM automation.
- Screen fallback: mss + OCR pipeline.
- Local model runtime: Ollama with Llama 3.1 as primary local model family.
- Voice STT: faster-whisper on CUDA.
- Voice TTS: Piper local TTS (pyttsx3 fallback during migration).
- Wake-word (later phase): openWakeWord (Porcupine optional alternative).
- Storage: SQLite + FTS5 for logs and memory.
- Optional service layer: FastAPI local server.
- Local container orchestration: Docker Compose (ash-api + ollama).

Routing policy:
- If browser task, use Playwright.
- Else if desktop app task, use OS automation.
- Else fallback to screenshot + vision pipeline.

## 7. Security and Privacy Baseline
- Keep sensitive context on-device by default.
- Encrypt local storage if credentials/tokens are included.
- Avoid storing raw secrets in logs.
- Add explicit opt-in for any cloud calls.

## 8. Reliability Baseline
- Deterministic execution for repeatable low-level actions.
- Model-driven planning with deterministic validation gates.
- Timeout, retry, and fallback policies per skill.

## 9. Frozen Architecture Decisions
- Runtime and packaging: local single-machine deployment for personal use.
- Model strategy: local-first hybrid, cloud disabled by default.
- Memory and indexing: SQLite-backed storage with lightweight indexing.
- Permission granularity: three-tier risk model with policy overlays.

Reference: Decision rationale is recorded in the Architecture Decision Log.
