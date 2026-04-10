# Roadmap And Milestones

## Planning Phase (Current)
Goal: freeze requirements and architecture before implementation.

Exit criteria:
- PRD approved.
- Architecture approved.
- Safety and risk strategy approved.
- Milestones and acceptance criteria approved.

## Phase 1: Foundation MVP
Objective: text-plus-voice assistant with safe desktop and browser actions.

Scope:
- Intent parsing and structured task planning.
- Push-to-talk voice command input and transcription.
- Basic desktop actions (open app, open folder, open website).
- Browser workflow support for a limited set of scenarios.
- Action confirmation model and execution logging.

Acceptance criteria:
- At least 10 predefined tasks completed reliably.
- Traceable logs for each execution.
- Confirmation prompts for risky actions.
- Voice command understanding at or above 85 percent on controlled MVP command set.

## Phase 2: Workflow Intelligence
Objective: make multi-step task completion more robust.

Scope:
- Task templates and reusable routines.
- Better failure recovery and fallback options.
- Preference memory and personalization basics.

Acceptance criteria:
- At least 20 supported tasks.
- Improved completion success and reduced manual correction.

## Phase 3: Natural Interaction Expansion
Objective: improve assistant feel and speed.

Scope:
- Always-on wake mode and stronger voice personalization.
- Richer conversational context handling.
- Faster execution pipeline and caching.

Acceptance criteria:
- Smooth end-to-end interaction for daily workflows.
- Noticeable reduction in user effort for repeated tasks.

## Phase 4: Advanced Companion Mode
Objective: transform into a dependable desktop partner.

Scope:
- Deeper productivity integrations.
- Proactive but controlled suggestions.
- Expanded policy and trust controls.

Acceptance criteria:
- Stable daily use with minimal correction.
- Clear trust and safety controls for autonomy limits.

## Milestone Risk Gates
Before moving to next phase:
- Reliability gate: success targets met.
- Safety gate: no unresolved high-risk behaviors.
- UX gate: interaction flow remains understandable.
- Privacy gate: data handling policy is enforced.

## Dependencies
- Stable automation layer.
- Well-defined skill contracts.
- Test scenario catalog and evaluation harness.
- Log instrumentation from day one.
