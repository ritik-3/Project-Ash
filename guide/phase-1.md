# Phase 1 Implementation Guide

This guide defines the full end-to-end implementation plan for Phase 1 of Ash: a basic conversational voice assistant that wakes up, listens, talks back, and keeps short session context. Phase 1 does **not** include desktop control, browser automation, task execution, reminders, file actions, or multi-step workflows.

The guide is based on the current project docs:
- [Project Structure](../docs/Project-Structure.md)
- [Tools and Tech](../docs/Tools-and-Tech.md)
- [System Specs](../System-Specs.md)
- [Requirements](../requirements.txt)

## Phase 1 Goal

Build a local-first conversational assistant that can:
- wake up using a wake word
- capture microphone input
- transcribe speech to text
- send text to a local LLM
- convert the response back to speech
- continue the conversation naturally
- remember the immediate session context only

The assistant should feel like a voice companion, not an automation tool.

## Phase 1 Scope

### In Scope
- Wake word detection
- Voice activity detection
- Speech-to-text
- Local LLM chat
- Text-to-speech
- Session-only conversational memory
- Basic conversation turn handling
- Simple FastAPI backend
- Simple local service startup on Windows

### Out of Scope
- Browser automation
- Desktop automation
- File operations
- Calendar, email, reminders, or productivity actions
- Long-term memory
- Tool routing for actions
- Multi-agent orchestration
- Cloud fallback logic unless used only as a future placeholder

## Phase 1 Success Criteria

Phase 1 is complete when all of the following are true:
1. The assistant can wake up with a wake word.
2. The assistant can listen to speech and transcribe it accurately enough for conversation.
3. The assistant can send text to a local model and receive a response.
4. The assistant can speak the response through speakers or headset.
5. The assistant can continue a short natural conversation across multiple turns.
6. The assistant can run locally on the current Windows 10 machine.
7. The assistant can start and stop cleanly without breaking the system.

## Recommended Phase 1 Stack

Use the tools already selected in [Tools and Tech](../docs/Tools-and-Tech.md):
- Ollama for the local model runtime
- llama3.1:8b-instruct as the first local model
- faster-whisper for speech-to-text
- piper-tts for text-to-speech
- openwakeword for wake word detection
- silero-vad for voice activity detection
- FastAPI for the backend service
- SQLite for lightweight session storage later if needed
- Python 3.11+ in the project virtual environment

## Phase 1 System Design

### Main Components
- Wake word listener: waits for activation phrase
- Audio capture service: records user speech from the selected input device
- VAD gate: decides when the user has started and stopped speaking
- STT service: converts speech into text
- Conversation service: manages turn-taking and prompt assembly
- LLM provider: sends the prompt to Ollama and gets the answer
- TTS service: speaks the answer aloud
- Session memory store: keeps recent turns for context
- API layer: exposes a health endpoint and conversation endpoints

### Conversation Loop
1. Wake word is detected.
2. Audio capture starts.
3. VAD detects speech boundaries.
4. STT transcribes the speech.
5. Conversation service formats the user message with recent history.
6. LLM provider generates a reply.
7. TTS speaks the reply.
8. Recent turns are stored in session memory.
9. The assistant waits for the next user turn.

## Suggested Phase 1 Folder Structure

The existing scaffold under [apps/assistant-api](../apps/assistant-api) should grow into a small but clean service layout:

```text
apps/assistant-api/
  app/
    api/
      v1/
        endpoints/
          health.py
          chat.py
          voice.py
    core/
      config.py
      logging.py
    providers/
      llm/
        base.py
        ollama_provider.py
      stt/
        base.py
        faster_whisper_provider.py
      tts/
        base.py
        piper_provider.py
      wakeword/
        base.py
        openwakeword_provider.py
      vad/
        base.py
        silero_provider.py
    services/
      conversation_service.py
      audio_service.py
      memory_service.py
    schemas/
      common.py
      chat.py
      voice.py
    middleware/
      error_handler.py
    main.py
  tests/
    unit/
    integration/
  README.md
```

This is enough for Phase 1. Avoid adding task, browser, or desktop capability folders yet.

## Implementation Phases Inside Phase 1

### Step 1: Lock the conversation rules
Define what Ash is allowed to do in Phase 1:
- talk naturally
- answer questions conversationally
- remember the current session context only
- ask clarifying questions when needed
- never execute system actions

Create a system prompt that gives Ash a stable personality:
- name: Ash
- female persona
- confident
- friendly
- slightly sarcastic
- concise but conversational
- voice-first

### Step 2: Build the backend skeleton
Use the current FastAPI scaffold as the base.

The backend should provide:
- `GET /api/v1/health`
- `POST /api/v1/chat`
- `POST /api/v1/voice` or a voice session endpoint

The backend is not the assistant itself. It is the service layer that coordinates the assistant loop.

### Step 3: Add configuration management
Expand `app/core/config.py` to hold:
- app name and version
- Ollama host and model name
- microphone and speaker preferences
- wake word settings
- VAD thresholds
- STT model choice
- TTS voice choice
- session memory size

Keep configuration in one place so the assistant can be tuned without code changes.

### Step 4: Implement the LLM provider abstraction
Phase 1 should use a provider interface so the chat engine is swappable later.

Minimum provider files:
- `app/providers/llm/base.py`
- `app/providers/llm/ollama_provider.py`

Responsibilities:
- accept the conversation prompt
- call Ollama locally
- return a plain text assistant reply
- expose clean errors if the model is unavailable

At this stage, do not build tool routing or multi-provider orchestration.

### Step 5: Implement speech-to-text
Add a speech-to-text service using faster-whisper.

Responsibilities:
- load the chosen transcription model
- accept recorded audio
- return transcribed text
- handle short and long utterances
- keep transcription latency low enough for conversation

Recommended behavior:
- start with a small or medium Whisper model variant that fits the machine well
- prefer reliable latency over maximum accuracy in Phase 1

### Step 6: Implement text-to-speech
Add a TTS service using Piper.

Responsibilities:
- accept assistant text
- convert text into audible speech
- support a stable natural voice
- keep playback smooth and clear

The TTS layer should be able to play directly through the default Windows audio device or a selected headset.

### Step 7: Implement wake word detection
Add wake word support using openWakeWord.

Responsibilities:
- keep listening in the background while the app is open
- detect the trigger phrase
- start a conversation turn only after wake word detection
- avoid spurious activations as much as possible

Phase 1 should not be always-on at the OS level if that is too heavy. It is enough for it to operate while the assistant app is running.

### Step 8: Implement voice activity detection
Add VAD using Silero VAD.

Responsibilities:
- detect when the user is speaking
- detect when speech ends
- reduce unnecessary transcription of silence
- make turn-taking feel natural

VAD should be used to avoid manually hitting record/stop for each turn.

### Step 9: Add session memory only
The assistant should remember the current conversation session.

Session memory should store:
- recent user messages
- recent assistant replies
- the current topic
- a small amount of recency context

Do not build long-term memory yet. Do not store personal profiles or persistent preferences yet. Phase 1 is only about short conversational continuity.

### Step 10: Add conversation orchestration
Create a `conversation_service.py` that coordinates the whole round trip.

Responsibilities:
- receive user text
- fetch recent session turns
- build the prompt
- call the LLM provider
- post-process the output
- send it to TTS
- append the turn to memory

This is the heart of Phase 1.

### Step 11: Add simple API endpoints
Keep the API small and clear.

Recommended endpoints:
- `GET /api/v1/health` for service status
- `POST /api/v1/chat` for typed conversation
- `POST /api/v1/voice/start` to begin a voice session
- `POST /api/v1/voice/stop` to end a voice session

If voice streaming is too much for the first pass, keep the interface simple and use chunked local handling inside the service.

### Step 12: Add logging and error handling
Add structured logs for:
- wake word detection
- transcription start and end
- model requests and model failures
- TTS generation and playback
- conversation timing

Errors should be readable and localized:
- if STT fails, say the system did not hear clearly
- if the model fails, retry once and then report a safe fallback message
- if TTS fails, return text on the screen and log the failure

### Step 13: Add tests
Phase 1 should include tests early, not later.

Minimum tests:
- unit test for prompt building
- unit test for session memory trimming
- unit test for provider abstraction
- integration test for health endpoint
- integration test for a chat round trip with mocked LLM
- integration test for a voice pipeline with mocked STT and TTS

### Step 14: Validate the full loop
Test the complete user experience:
1. Start the app.
2. Say the wake word.
3. Speak a sentence.
4. Verify it is transcribed.
5. Verify the response is generated.
6. Verify the response is spoken.
7. Ask a follow-up question.
8. Verify the assistant remembers the immediate context.

If any step feels broken, fix that before moving to Phase 2.

## Implementation Order

Follow this order to avoid rework:
1. Finalize system prompt and conversation behavior.
2. Implement FastAPI app startup and health route.
3. Add Ollama provider.
4. Add typed chat endpoint.
5. Add STT.
6. Add TTS.
7. Add wake word detection.
8. Add VAD.
9. Add session memory.
10. Add end-to-end orchestration.
11. Add tests.
12. Add packaging and startup scripts.

## Suggested Environment Variables

Create a local `.env` file later with values such as:
- `APP_NAME=Ash Assistant`
- `APP_VERSION=0.1.0`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3.1:8b-instruct`
- `VOICE_STT_MODEL=small`
- `VOICE_TTS_VOICE=default`
- `WAKE_WORD=hey assistant`
- `SESSION_MEMORY_LIMIT=12`

## Local Run Strategy

Phase 1 should run locally with one command.

Recommended dev startup:
```powershell
Set-Location c:\Ashu\Project-Ash\apps\assistant-api
..\..\.venv\Scripts\Activate.ps1
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

If you later add a small tray app or background runner, keep the backend as a separate service process.

## Quality Checks Before Phase 2

Do not move on until these are true:
- wake word works reliably enough
- the assistant responds in voice
- short conversations remain coherent
- the app launches cleanly on Windows
- basic errors are handled without crashing
- tests pass for the core conversation flow

## Phase 1 Definition of Done

Phase 1 is done when Ash can:
- wake up by voice
- listen to the user
- transcribe speech
- answer in a natural voice
- keep a short conversation going
- run locally on the current machine
- do all of this without task execution or automation

That is the complete Phase 1 baseline.
