# Ash Assistant - Scalable End-to-End Project Structure

This document defines the full project structure for a scalable, hybrid (local-first + cloud fallback) desktop AI assistant.

## Architecture Goals
- Modular: every capability can evolve independently.
- Scalable: easy to grow from single-user desktop to multi-service architecture.
- Safe: Level 2 autonomy with confirmation before actions.
- Observable: logs, metrics, traces, and clear failure reporting.
- Testable: clear separation between interfaces, orchestration, and tool adapters.

## High-Level Architecture
- Interface Layer: voice, chat, optional desktop UI.
- Orchestration Layer: routing, planning, policy checks, action execution.
- Intelligence Layer: local LLM + cloud fallback.
- Capability Layer: browser, desktop, productivity, scheduling actions.
- Data Layer: memory, task history, settings, telemetry.

## Recommended Repository Layout
```text
Project-Ash/
  apps/
    assistant-api/
      app/
        api/
          v1/
            endpoints/
              health.py
              chat.py
              voice.py
              tasks.py
              memory.py
              actions.py
            router.py
        core/
          config.py
          logging.py
          security.py
          lifecycle.py
        schemas/
          chat.py
          voice.py
          task.py
          memory.py
          common.py
        services/
          conversation_service.py
          orchestration_service.py
          policy_service.py
          memory_service.py
          briefing_service.py
        repositories/
          memory_repository.py
          task_repository.py
          event_repository.py
          settings_repository.py
        providers/
          llm/
            base.py
            ollama_provider.py
            gemini_provider.py
            router.py
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
        capabilities/
          browser/
            playwright_client.py
            browser_actions.py
          desktop/
            pywinauto_client.py
            desktop_actions.py
          productivity/
            planner_actions.py
            reminders_actions.py
            doc_actions.py
          system/
            app_launcher.py
            window_switcher.py
            file_search.py
        orchestration/
          intent_classifier.py
          task_planner.py
          action_executor.py
          confirmation_manager.py
          retry_manager.py
          fallback_manager.py
        memory/
          short_term_store.py
          long_term_store.py
          project_context_store.py
          memory_controls.py
        workers/
          scheduler_worker.py
          event_worker.py
          digest_worker.py
        db/
          models/
            memory.py
            task.py
            event.py
            setting.py
          migrations/
          session.py
        middleware/
          request_id.py
          error_handler.py
          timing.py
          auth_guard.py
        main.py
      tests/
        unit/
          test_orchestration.py
          test_memory.py
          test_policy.py
        integration/
          test_chat_flow.py
          test_voice_flow.py
          test_task_execution.py
        e2e/
          test_browser_automation.py
          test_desktop_actions.py
      pyproject.toml
      README.md

    assistant-ui/
      src/
        components/
        pages/
        hooks/
        services/
      public/
      package.json
      README.md

  packages/
    shared-contracts/
      assistant_events.json
      api_contracts.json
      action_contracts.json
      README.md

    prompts/
      system/
        core_personality.txt
        safety_policy.txt
      task/
        browser_task_prompt.txt
        study_task_prompt.txt
        coding_task_prompt.txt
      router/
        model_routing_prompt.txt
      README.md

    sdk/
      python/
        ash_sdk/
      README.md

  infra/
    docker/
      assistant-api.Dockerfile
      worker.Dockerfile
    scripts/
      bootstrap.ps1
      run_local.ps1
      check_env.ps1
      seed_data.ps1
    ci/
      github-actions/
        lint.yml
        test.yml
        build.yml

  configs/
    environments/
      .env.example
      dev.env.example
      prod.env.example
    model/
      ollama_models.yaml
      routing_policy.yaml
    voice/
      stt_config.yaml
      tts_config.yaml
      wakeword_config.yaml

  data/
    sqlite/
      ash.db
    cache/
    exports/
    backups/

  docs/
    architecture/
      system-overview.md
      sequence-diagrams.md
      scaling-strategy.md
    product/
      Idea.md
      Tools-and-Tech.md
      System-Specs.md
      Project-Structure.md
    runbooks/
      local-setup.md
      incident-recovery.md
      backup-restore.md

  observability/
    logs/
    metrics/
    traces/
    dashboards/

  .gitignore
  requirements.txt
  README.md
```

## Execution Flow (End-to-End)
1. User speaks or types command.
2. Voice pipeline converts speech to text (if voice input).
3. Orchestrator classifies intent and builds task plan.
4. Policy service checks safety and confirmation requirements.
5. Action executor triggers capabilities (browser, desktop, system).
6. Result is stored in memory and task history.
7. Response is generated (local LLM first, cloud fallback if needed).
8. Voice output is spoken by TTS when enabled.

## Scale Path
- Phase 1 (Single process): API + workers + SQLite in one machine.
- Phase 2 (Modular local services): separate voice, orchestration, and action workers.
- Phase 3 (Distributed): split providers, workers, and API with message queue.
- Phase 4 (Multi-device): sync memory/settings across trusted endpoints.

## Core Design Rules
- Keep provider interfaces abstract so LLM/STT/TTS engines are swappable.
- Keep capabilities isolated from orchestration logic.
- Keep policies centralized and enforce before every side-effect action.
- Keep memory writes versioned and auditable.
- Keep retries and fallback logic explicit, not hidden inside adapters.

## Testing Strategy
- Unit tests: planners, policies, memory logic, routing logic.
- Integration tests: API + DB + provider mocks.
- E2E tests: browser and desktop automation flows.
- Reliability tests: fallback behavior, timeout handling, retry policy.
- Performance tests: latency budgets for voice and response generation.

## Deployment Modes
- Local Development: all services on one Windows machine.
- Local Production: persistent background service with startup scripts.
- Hybrid Production: local core runtime with cloud fallback endpoints.

## Immediate Next Build Order
1. Create `apps/assistant-api/app` skeleton.
2. Implement `core/config.py`, `core/logging.py`, and `main.py`.
3. Add provider interfaces and Ollama provider.
4. Add conversation endpoint and orchestration service.
5. Add memory service with SQLite repositories.
6. Add voice pipeline (wakeword -> STT -> orchestrator -> TTS).
7. Add browser and desktop capability adapters.
8. Add tests, telemetry, and retry/fallback hardening.
