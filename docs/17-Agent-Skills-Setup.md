# Agent Skills Setup (skills.sh)

## Purpose
Define how Project Ash uses skills.sh to improve coding efficiency and quality for this stack.

## Verified skills.sh basics
- Skills are reusable agent capabilities.
- Install and manage via npx skills commands.
- Skills can be project-level and agent-targeted.

## Commands Used In This Project
- npx skills --help
- npx skills find fastapi
- npx skills find playwright
- npx skills find docker
- npx skills find react typescript
- npx skills init project-ash-skill-kit
- npx skills add wshobson/agents@fastapi-templates -y
- npx skills add currents-dev/playwright-best-practices-skill@playwright-best-practices -y
- npx skills add sickn33/antigravity-awesome-skills@docker-expert -y
- npx skills add dotneet/claude-code-marketplace@typescript-react-reviewer -y
- npx skills list

## Installed Project Skills
- fastapi-templates
  - Source: wshobson/agents@fastapi-templates
  - Focus: FastAPI patterns and templates
- playwright-best-practices
  - Source: currents-dev/playwright-best-practices-skill@playwright-best-practices
  - Focus: Playwright automation quality
- docker-expert
  - Source: sickn33/antigravity-awesome-skills@docker-expert
  - Focus: Docker and container best practices
- typescript-react-reviewer
  - Source: dotneet/claude-code-marketplace@typescript-react-reviewer
  - Focus: React + TypeScript code quality

## Local Project Skill Scaffold
- Initialized local skill scaffold:
  - project-ash-skill-kit/SKILL.md
- Use this for Project Ash-specific workflows:
  - Risk-gated execution checks
  - Routing policy checks (browser, desktop, vision fallback)
  - Voice pipeline integration checklist

## How We Will Use These Skills
1. Backend tasks:
- Apply fastapi-templates guidance for endpoint structure and validation.

2. Browser automation tasks:
- Apply playwright-best-practices before modifying browser task code.

3. Infra and container tasks:
- Apply docker-expert guidance for Dockerfile and compose improvements.

4. Frontend tasks:
- Apply typescript-react-reviewer once UI app is scaffolded.

## Operational Notes
- Skills run with broad agent permissions; review source and behavior before relying on them in sensitive areas.
- Keep a small, curated skill set aligned to architecture decisions.
- Update skills periodically with npx skills update.

## Current Status
- Skills installed successfully for this project.
- One update attempt for find-skills failed during global update check; installed project skills remain available.
