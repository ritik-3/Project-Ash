# Project Ash OpenClaw-Style Features: End-to-End Implementation Guide

## 1. Purpose
This document defines a complete implementation path for adding OpenClaw-like capabilities to Project Ash while preserving its local-first, risk-gated, and documentation-driven design.

Target outcomes:
- Multi-channel control through messaging apps.
- Autonomous scheduled/background task execution.
- Extensible skill ecosystem with permission boundaries.
- Strong safety, privacy, and security posture for self-hosted deployment.

This guide is implementation-ready and aligned with the current architecture and docs in this repository.

## 2. Current Baseline (What Already Exists)
Project Ash already has the core building blocks required:
- Intent parsing, planning, and execution orchestration.
- Risk classification and confirmation gates.
- Browser, desktop, and vision fallback routing.
- Local API server and task history in SQLite.
- Existing docs for architecture, rollout, and safety.

Relevant existing files:
- src/project_ash/orchestrator.py
- src/project_ash/planner.py
- src/project_ash/executor.py
- src/project_ash/risk.py
- src/project_ash/api/server.py
- src/project_ash/memory/sqlite_store.py
- docs/02-System-Architecture.md
- docs/05-Risks-Safety-Privacy.md

## 3. Feature Scope for OpenClaw-Like Expansion

### 3.1 In Scope
- Channel connectors:
  - Telegram Bot
  - Slack App
  - Discord Bot
  - WhatsApp via provider abstraction
- Asynchronous job execution:
  - Scheduled tasks
  - Retryable background tasks
  - Periodic routines
- Skill registry:
  - Install/enable/disable skills
  - Manifest-based permission model
  - Skill risk metadata
- Governance and hardening:
  - Secret storage isolation
  - Prompt injection checks
  - Audit logs and approval records

### 3.2 Out of Scope (Initial Release)
- Fully unsupervised high-risk operations.
- Autonomous financial or irreversible transactions.
- Running untrusted code/skills without sandbox and signature policy.

## 4. Target Architecture Additions

### 4.1 New Components
1. Channel Gateway Layer
- Receives channel events/webhooks.
- Normalizes messages into a common input envelope.
- Maps channel identity to local user/profile.

2. Autonomy Engine
- Scheduler for timed and recurring jobs.
- Queue worker for asynchronous execution.
- Job state tracking and cancellation controls.

3. Skill Registry + Policy Guard
- Manages skill manifests and permissions.
- Enforces allowlist/denylist and risk policy before action execution.

4. Security Envelope
- Secret manager adapter.
- Content sanitization + prompt injection detector.
- Signed audit trail for sensitive actions.

### 4.2 Updated Data Flow
1. Message/event arrives from channel connector.
2. Channel Gateway creates normalized request envelope.
3. Safety prefilter scans content for injection patterns and policy violations.
4. Orchestrator creates plan.
5. Policy Guard validates each plan step against:
- Risk level
- Skill permissions
- Channel permissions
- User approval requirements
6. If immediate task: execute now.
7. If scheduled/autonomous task: enqueue into Autonomy Engine.
8. Worker executes step-wise through existing executor/router.
9. Results and audit records are persisted; status pushed back to channel.

## 5. Repository Change Plan

## 5.1 New Python Modules
Create these files:
- src/project_ash/channels/__init__.py
- src/project_ash/channels/base.py
- src/project_ash/channels/telegram.py
- src/project_ash/channels/slack.py
- src/project_ash/channels/discord.py
- src/project_ash/channels/whatsapp.py
- src/project_ash/channels/router.py

- src/project_ash/autonomy/__init__.py
- src/project_ash/autonomy/models.py
- src/project_ash/autonomy/scheduler.py
- src/project_ash/autonomy/queue.py
- src/project_ash/autonomy/worker.py

- src/project_ash/skills/registry.py
- src/project_ash/skills/manifest.py
- src/project_ash/skills/policy.py

- src/project_ash/security/__init__.py
- src/project_ash/security/secrets.py
- src/project_ash/security/sanitizer.py
- src/project_ash/security/injection_guard.py
- src/project_ash/security/audit.py

### 5.2 Updates to Existing Files
- src/project_ash/models.py
  - Add channel/session/job/approval models.
- src/project_ash/risk.py
  - Add autonomous-mode risk policy branch.
- src/project_ash/planner.py
  - Add plan step tags for scheduled and async execution.
- src/project_ash/orchestrator.py
  - Add queue handoff mode and channel-aware context.
- src/project_ash/executor.py
  - Add policy checkpoint hook before action dispatch.
- src/project_ash/api/server.py
  - Add channel webhook routes, job APIs, skill APIs, approval APIs.
- src/project_ash/config.py
  - Add channel config and security defaults.

### 5.3 New Tests
- tests/test_channels_router.py
- tests/test_channel_telegram_webhook.py
- tests/test_autonomy_scheduler.py
- tests/test_autonomy_worker.py
- tests/test_skill_manifest_policy.py
- tests/test_security_injection_guard.py
- tests/test_api_jobs.py
- tests/test_api_approvals.py
- tests/test_end_to_end_channel_to_execution.py

## 6. Contracts and Schemas

### 6.1 Normalized Channel Envelope
Use a channel-agnostic envelope:
- envelope_id
- channel_type: telegram | slack | discord | whatsapp
- channel_user_id
- channel_conversation_id
- timestamp_utc
- message_text
- attachments
- metadata

### 6.2 Job Model
- job_id
- owner_user_id
- source: direct | scheduled | autonomous_rule
- intent_text
- plan_snapshot
- risk_level
- status: queued | running | waiting_approval | completed | failed | canceled
- run_at_utc
- retry_count
- last_error

### 6.3 Approval Record
- approval_id
- job_id
- required_for_risk
- prompt_summary
- decision: approved | denied | expired
- decided_by
- decided_at_utc

### 6.4 Skill Manifest (YAML/JSON)
Each skill must declare:
- name
- version
- description
- actions_exposed
- required_permissions
- risk_level_default
- external_scopes (mail/calendar/files/etc.)
- network_policy (none | allowlist)
- requires_confirmation (bool)
- maintainer_signature (optional in phase 1, required in phase 2)

## 7. API Expansion Plan (FastAPI)

### 7.1 Channel APIs
- POST /channels/webhook/{provider}
- POST /channels/send
- GET /channels/health

### 7.2 Job APIs
- POST /jobs
- GET /jobs/{job_id}
- GET /jobs
- POST /jobs/{job_id}/cancel
- POST /jobs/{job_id}/retry

### 7.3 Scheduler APIs
- POST /schedules
- GET /schedules
- DELETE /schedules/{schedule_id}

### 7.4 Skill Registry APIs
- GET /skills
- POST /skills/install
- POST /skills/{skill_name}/enable
- POST /skills/{skill_name}/disable
- GET /skills/{skill_name}/manifest

### 7.5 Approval APIs
- POST /approvals/{job_id}/approve
- POST /approvals/{job_id}/deny
- GET /approvals/pending

## 8. Implementation Sequence (Execution Plan)

### Phase 0: Foundation and Contracts
- Add models for envelopes/jobs/approvals/manifests.
- Add migration support in SQLite store.
- Add API contract tests for new endpoints.

Exit criteria:
- New schemas validated.
- DB migration succeeds on clean and existing DB.

### Phase 1: Channel Gateway
- Implement base connector interface.
- Deliver Telegram first (lowest setup friction).
- Add channel router and inbound event normalization.

Exit criteria:
- Telegram inbound message can trigger plan/execute path.
- Response is returned to originating chat reliably.

### Phase 2: Autonomy Engine
- Implement queue tables and worker lifecycle.
- Add scheduler for one-time and recurring jobs.
- Add runtime state for job cancellation/retry.

Exit criteria:
- Scheduled tasks execute at expected time.
- Failed tasks retry using backoff policy.

### Phase 3: Skill Registry + Policy Guard
- Implement manifest parser and validation.
- Enforce permissions in executor pre-dispatch hook.
- Add install/enable/disable APIs.

Exit criteria:
- Unauthorized actions are blocked by policy with audit logs.
- Skills can be safely toggled at runtime.

### Phase 4: Security Hardening
- Add secret manager adapter and env fallbacks.
- Add injection guard before planning and before tool call.
- Add irreversible action two-step confirmation policy.

Exit criteria:
- Red-team prompts cannot bypass confirmation policy.
- Secrets are never logged in plaintext.

### Phase 5: Additional Channels
- Add Slack and Discord.
- Add WhatsApp provider abstraction.
- Add channel-specific rate limit and message formatting.

Exit criteria:
- Same user intent behaves consistently across all channels.

### Phase 6: E2E Stability and Rollout
- Add E2E tests from channel input to final action result.
- Add observability dashboards and failure alerts.
- Stage rollout by capability/risk.

Exit criteria:
- Target success rate reached.
- No unresolved critical safety findings.

## 9. Database and Migration Plan
Use migration scripts for SQLite schema evolution.

Required tables (new):
- channel_sessions
- jobs
- job_attempts
- schedules
- approvals
- skills_registry
- skill_events
- security_audit_events

Indexes (minimum):
- jobs(status, run_at_utc)
- approvals(job_id, decision)
- security_audit_events(created_at_utc)
- skills_registry(name, enabled)

Retention:
- Keep detailed job attempts 30-90 days.
- Keep security audits longer per user policy.

## 10. Security, Privacy, and Isolation

### 10.1 Baseline Controls
- Default deny for high-risk autonomous actions.
- Mandatory confirmation for medium/high actions.
- Per-channel token scope minimization.
- Redaction filter for logs and API responses.

### 10.2 Prompt Injection Defenses
Add checks at two points:
- Before planning (sanitize user and external content).
- Before execution (validate plan step against policy and expected schema).

Hard rules:
- Never execute instructions that override system policy.
- Never auto-run embedded tool instructions from web/email content.
- Never expose secrets/tokens in model context.

### 10.3 Runtime Isolation
Recommended runtime:
- Containerized service for API/orchestrator/worker.
- Separate container/network for model runtime where practical.
- Read-only root filesystem where possible.
- Non-root user for all containers.

## 11. Docker and Deployment Guide

### 11.1 Compose Topology
Services:
- ash-api
- ash-worker
- ash-scheduler
- ollama (optional local model service)

Operational requirements:
- Health checks for each service.
- Resource limits for API and workers.
- Persisted volumes for SQLite and model data.
- Secret injection via env files or secret provider adapter.

### 11.2 Deployment Modes
- Local dev: single compose profile.
- Personal prod (self-hosted): hardened compose profile with locked ports and strict firewall.

## 12. Observability and Operations

### 12.1 Logging
Structured JSON logs with fields:
- request_id
- envelope_id
- job_id
- plan_id
- action
- risk_level
- policy_decision
- latency_ms
- result

### 12.2 Metrics
Minimum metrics:
- plan_creation_latency
- job_queue_depth
- job_success_rate
- job_failure_rate_by_action
- approval_required_count
- policy_block_count

### 12.3 Alerting
Alert on:
- repeated policy bypass attempts
- queue backlog over threshold
- channel webhook failures
- elevated high-risk denials

## 13. Testing Strategy (End to End)

### 13.1 Unit Tests
- schema validation
- manifest parser
- policy decision matrix
- scheduler next-run computation
- injection detector rule matching

### 13.2 Integration Tests
- webhook ingestion to normalized envelope
- queue enqueue/dequeue lifecycle
- approval workflow transitions
- skill enable/disable behavior

### 13.3 E2E Tests
Core E2E scenarios:
1. Telegram message -> planning -> low-risk execution -> reply posted.
2. Telegram message -> medium-risk execution -> approval requested -> approved -> execution done.
3. Scheduled task triggers at time -> execution succeeds -> summary delivered.
4. Prompt injection payload -> blocked by policy -> incident logged.

### 13.4 Non-Functional Tests
- load testing for webhook throughput.
- recovery testing (worker restart with in-flight jobs).
- security checks for token leakage.

## 14. Rollout and Governance

### 14.1 Rollout Stages
- Stage A: Telegram only, low-risk actions only.
- Stage B: Add scheduler with medium-risk approvals.
- Stage C: Add Slack/Discord and skill registry.
- Stage D: Enable curated autonomous routines.

### 14.2 Governance Rules
- Feature flags for each channel and risky capability.
- All high-risk capability changes require updated tests and docs.
- Security review required before enabling third-party skills.

## 15. Acceptance Criteria
Release is accepted when all are true:
- Multi-channel messaging works for at least Telegram plus one additional channel.
- Scheduled/background jobs run with retry and cancellation.
- Skill policy enforcement blocks unauthorized actions reliably.
- No critical security findings in prompt injection test pack.
- Full audit trail exists for all medium/high-risk actions.

## 16. Task Checklist (Implementation Tracker)

### 16.1 Build Tasks
- Add channel envelopes, jobs, approvals, and skill manifest models.
- Build channel connector abstraction.
- Implement Telegram connector and router.
- Build queue + scheduler + worker.
- Build skill registry and policy guard.
- Add security sanitizer + injection guard + audit logger.
- Expand API and wire orchestration hooks.

### 16.2 Verification Tasks
- Add unit, integration, and E2E test suites.
- Validate policy matrix for all action families.
- Validate DB migration and rollback safety.
- Validate deployment compose with health checks.

### 16.3 Documentation Tasks
- Update architecture docs with new layers.
- Update safety/risk docs with autonomous controls.
- Update rollout and incident response playbooks.

## 17. Immediate Next Step
Start with Phase 0 contract implementation first (models + DB migration + API contract tests), then deliver Telegram connector in isolation before introducing autonomy and multi-channel expansion.
