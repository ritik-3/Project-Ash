# Governance And Change Control

## Purpose
Control scope, safety, and quality as Project Ash evolves beyond initial implementation.

## Ownership
- Product Owner: Ashu (scope and priority decisions)
- Technical Owner: Implementation maintainer
- Safety Owner: Policy and risk approval owner

For personal single-user mode, one person may hold all three roles.

## Change Request Process
1. Submit change request with objective and impacted capabilities.
2. Classify impact: Low, Medium, High risk.
3. Assess documentation impact (PRD, architecture, safety, roadmap).
4. Define test impact and acceptance criteria updates.
5. Approve or reject.
6. Implement only after approval record is logged.

## Approval Rules
- Low impact: Product Owner approval.
- Medium impact: Product + Technical Owner approval.
- High impact or safety impact: Product + Technical + Safety approval.

## Mandatory Change Record Fields
- Change ID
- Date
- Requested by
- Description
- Risk classification
- Affected documents
- Affected tests
- Approval decision
- Rollback plan

## Document Update Policy
- If behavior changes, update docs before or with code change.
- If safety policy changes, update risk and decision logs first.
- If capability scope changes, update task catalog and command catalog.

## Release Control
- Each release requires:
  - Updated changelog
  - Passed test gate
  - Safety review sign-off for medium/high risk changes

## Incident Governance
- Log incident within 24 hours.
- Freeze related risky capability until reviewed.
- Add regression test before re-enabling.

## Audit Cadence
- Weekly: review logs and incidents.
- Monthly: review scope drift and policy compliance.
