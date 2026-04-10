# Target Tech Stack And Step-by-Step Execution Plan

## Hardware Profile
- CPU: Ryzen 5 2600
- GPU: RTX 3060 12GB
- RAM: 16GB DDR4 3600
- Storage: 520GB NVMe SSD

This profile is suitable for local-first assistant execution with quantized Llama 3.1 and CUDA speech recognition.

## Frozen Target Stack

### Core Runtime
- Python 3.10+
- Orchestration and policy in Project Ash runtime

### Local LLM
- Provider: Ollama
- Model family: Llama 3.1
- Recommended initial model variant: 8B quantized profile that fits local VRAM budget

### Voice
- STT: faster-whisper with CUDA
- TTS: Piper (local)
- Wake word (optional): openWakeWord (Porcupine optional)

### Automation And Vision
- Browser: Playwright
- Desktop apps: pywinauto + UI Automation
- Vision fallback: mss + OCR (EasyOCR or PaddleOCR)

### Memory And Storage
- SQLite + FTS5 for logs, task history, and preference memory
- Optional vector store only after semantic memory use cases are validated

### Local Service Layer
- FastAPI local server for UI/API boundary
- CLI and desktop UI can call local API endpoints

## Deterministic Routing Rule
1. If browser task, route to Playwright DOM control.
2. Else if desktop app task, route to OS automation.
3. Else route to screenshot + OCR vision fallback.

## Step-by-Step Implementation Sequence
1. LLM integration:
- Connect orchestrator prompt generation to Ollama adapter.
- Validate local response latency and output format.

2. Local STT migration:
- Replace cloud recognizer path with faster-whisper primary path.
- Keep temporary fallback only for development continuity.

3. Local TTS migration:
- Make Piper primary speech output engine.
- Keep pyttsx3 optional fallback until Piper voice packs are finalized.

4. Routing integration:
- Apply deterministic route selection before action execution.
- Record route decision in logs.

5. Automation adapters:
- Implement Playwright adapter for browser workflows.
- Implement pywinauto adapter for desktop workflows.

6. Vision fallback:
- Capture screenshot with mss.
- Extract text with OCR.
- Use fallback only when browser/desktop targeting fails.

7. Memory migration:
- Move task history to SQLite FTS5-backed store.
- Add preference memory tables and retention cleanup jobs.

8. Service layer:
- Expose assist endpoints via FastAPI.
- Keep CLI as first client.

9. Hardening:
- Add scenario tests based on command catalog.
- Validate risk-gate behavior across all action routes.

## Acceptance Targets
- Local LLM responses stable for task planning prompts.
- Voice transcription and response path fully local.
- Routing policy always resolved deterministically.
- Task logs searchable via SQLite FTS5.
- Browser and desktop action paths both validated on Windows.
