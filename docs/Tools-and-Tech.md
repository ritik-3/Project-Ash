# Tools and Tech Stack

This file defines the tools we will use for the Ash desktop assistant project.

## Project Direction
- Architecture: hybrid (local-first + cloud fallback)
- Budget: free tools only
- OS target: Windows 10
- Primary runtime: local LLM via Ollama
- Primary local model: llama3.1:8b-instruct
- Cloud fallback provider: Gemini Pro

## What You Already Have
- GPT Go subscription (manual use)
- Gemini Pro access (cloud fallback)
- Hardware: Ryzen 5 2600, RTX 3060, 16 GB RAM

## Core Tools (Install First)

### 1. LLM Runtime
- Ollama (primary local model server)

### 2. Backend and Orchestration
- Python 3.11+
- FastAPI (assistant service API)
- Uvicorn (ASGI server)
- Pydantic (structured configs and schemas)
- APScheduler (timed jobs like daily briefing)
- python-dotenv (environment variable management)

### 3. Voice Stack
- faster-whisper (speech-to-text)
- piper-tts (text-to-speech)
- openwakeword (wake word detection)
- silero-vad (voice activity detection)
- sounddevice + soundfile (audio I/O)

### 4. Computer Control and Automation
- Playwright (browser automation)
- pywinauto (desktop UI automation)
- pygetwindow (window switching/basic control)
- pyautogui (fallback desktop interactions)

### 5. Memory and Storage
- SQLite (local memory and logs)
- SQLAlchemy (database layer)

### 6. Utility and Reliability
- tenacity (retry/fallback behavior)
- loguru (structured logging)
- rich (dev console output)

## Final Model (Ollama)
- llama3.1:8b-instruct

## Cloud Fallback Strategy
- Primary: local model through Ollama
- Fallback: Gemini Pro for complex reasoning requests
- Use cloud only when local confidence is low or tasks are too complex

## Install Order (Practical)
1. Install Python 3.11+
2. Install Ollama
3. Pull one local model in Ollama
4. Create Python virtual environment
5. Install backend + voice + automation dependencies
6. Install Playwright browsers
7. Run a minimal voice loop test
8. Run browser and desktop action smoke tests

## Quick Setup Commands (Windows PowerShell)
```powershell
# 1) Create project venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Upgrade pip
python -m pip install --upgrade pip

# 3) Install base Python dependencies
pip install fastapi uvicorn pydantic apscheduler python-dotenv sqlalchemy tenacity loguru rich

# 4) Install voice stack
pip install faster-whisper piper-tts openwakeword silero-vad sounddevice soundfile

# 5) Install automation tools
pip install playwright pywinauto pygetwindow pyautogui
playwright install
```

## Notes and Constraints
- Keep the assistant in Level 2 autonomy (confirm before actions).
- Wake word/listening mode should run only when the app is open.
- Default voice setup should support both headset and desktop mic.
- Keep implementation modular so cloud providers can be swapped later.
