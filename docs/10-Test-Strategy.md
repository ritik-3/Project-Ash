# Test Strategy

## Objective
Validate that Project Ash is safe, reliable, and useful for day-to-day desktop productivity before broader use.

## Test Layers

### 1) Unit Tests
Scope:
- NLU normalization and intent parsing.
- Risk classification and confirmation rules.
- Plan generation for supported intents.

Target:
- High coverage for core decision logic.

### 2) Integration Tests
Scope:
- End-to-end flow from user input to execution plan to action result.
- Confirmation gating for medium/high risk actions.
- Task logging format and persistence.

Target:
- All P1 capability flows validated in controlled environment.

### 3) Scenario Tests (User-Centric)
Scope:
- Real command sequences from Top Voice Command Catalog.
- Casual phrasing, mixed-language phrasing, and imperfect grammar.
- Recovery behavior on errors and unclear commands.

Target:
- At least 20 core scenarios pass.

### 4) Safety Tests
Scope:
- Risk classification correctness.
- Block/confirm behavior for sensitive actions.
- Prevention of silent high-risk execution.

Target:
- Zero known bypass for high-risk confirmation gate.

## Quality Gates
- Unit tests pass.
- No critical/high severity defects unresolved.
- Voice understanding target achieved for controlled scenarios.
- Task logs generated for all execution attempts.

## Metrics
- Intent accuracy by command family.
- Task success rate.
- Clarification rate.
- Unsafe action prevention rate.
- Mean time to completion for P1 tasks.

## Test Data
- Command sets from command catalog.
- Positive and negative phrasing variants.
- Mixed-language command variants.

## Environment
- Primary test environment: Windows local machine.
- Browser: Chrome or Edge baseline.
- Audio input: standard laptop headset/microphone.

## Defect Severity
- Critical: Safety breach or irreversible wrong action.
- High: Wrong task execution with user-visible impact.
- Medium: Partial completion or frequent clarification loops.
- Low: Minor wording or UX issues.

## Exit Criteria For MVP
- All critical/high defects closed.
- Minimum success targets met on P1 scenarios.
- Safety suite passes without confirmation bypass.
