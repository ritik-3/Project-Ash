# assistant-api

FastAPI service for Ash Assistant.

## Purpose

This service is the backend entry point for the assistant. It currently provides a health endpoint and the base wiring for configuration, logging, routing, middleware, providers, and orchestration services.

## Run Locally

```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## First-Time Setup (Windows)

1. Copy `.env.example` to `.env` in this folder.
2. Start Ollama and pull the model configured in `.env`.
3. Start the API with:

```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
.\scripts\start_local.ps1
```

Use auto-reload only when actively editing backend code:

```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
.\scripts\start_local.ps1 -Reload
```

4. In a second terminal, list audio devices and set `AUDIO_INPUT_DEVICE` and `AUDIO_OUTPUT_DEVICE` in `.env` if needed:

```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
.\scripts\list_devices.ps1
```

5. Trigger one live turn:

```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
.\scripts\voice_turn.ps1
```

## Web UI

After starting the API, open:

- `http://127.0.0.1:8000/`

The web UI provides:

- live status (idle, active, busy, error)
- center orb that reacts to microphone energy
- typed chat against `/api/v1/chat`
- voice turn trigger against `/api/v1/voice/turn`

## API

- `GET /api/v1/health` returns a simple service status payload.
- `GET /api/v1/voice/devices` returns detected local audio devices.
- `POST /api/v1/voice/turn` executes one wake-listen-respond voice turn.

## Current Structure

- `app/main.py` - FastAPI application entry point
- `app/core` - configuration and logging helpers
- `app/api/v1` - HTTP routing and endpoints
- `app/providers` - model integration abstractions
- `app/services` - orchestration logic
- `app/middleware` - app-wide handlers
- `app/schemas` - shared request and response models

## Dependencies

Install the root `requirements.txt` from the repository root before running the service.

## Notes

- If `PIPER_VOICE_MODEL_PATH` is not set, TTS falls back to Windows SAPI.
- openWakeWord model assets are auto-downloaded on first use.