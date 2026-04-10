# Rollout Plan

## Objective
Ship Project Ash in controlled stages while preserving safety, reliability, and user trust.

## Stage 0: Local Developer Validation
- Run unit and integration tests.
- Validate key P1 tasks manually.
- Confirm logging and confirmation behavior.

Exit criteria:
- No critical defects.
- Core workflow stable in repeated runs.

## Stage 1: Personal Alpha (Single User)
- Enable daily use for limited time windows.
- Restrict automation to allowlisted tasks.
- Capture friction and correction cases.

Exit criteria:
- Stable operation for one week.
- No high-risk safety incidents.

## Stage 2: Expanded Personal Beta
- Expand command catalog coverage.
- Enable more browser and sheet workflows.
- Tune prompts and clarifications from observed data.

Exit criteria:
- Target success and satisfaction metrics achieved.
- Error recovery quality accepted.

## Stage 3: Stable Personal Release
- Freeze MVP capability set.
- Finalize documentation and backup process.
- Mark release baseline and change control start.

Exit criteria:
- Planning, testing, and governance checklists complete.
- Release notes and known limitations documented.

## Rollback Strategy
- Keep previous stable build available.
- Disable newly introduced risky actions first.
- Restore prior stable configuration when regressions appear.

## Monitoring During Rollout
- Daily review of task logs.
- Weekly summary of success rate and correction rate.
- Track incident count and severity.

## Communication Template (Personal Use)
For each rollout stage, document:
- Date and version
- Enabled capabilities
- Known issues
- New risks introduced
- Rollback trigger
