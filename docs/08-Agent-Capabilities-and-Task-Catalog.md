# Agent Capabilities And Task Catalog (MVP Focus)

## Purpose
Define exactly what Project Ash should do for normal daily usage before implementation.

## Core Role
Project Ash is an action assistant for everyday PC work.
It should understand instructions, perform the task, and report progress clearly.

## Capability Groups

### 0) Voice And Natural Language Control
What it does:
- Accept push-to-talk voice commands.
- Understand normal conversational phrasing and casual grammar.
- Handle mixed-language productivity instructions for common tasks.
- Answer naturally and clearly in step-by-step style for task execution.

Example commands:
- Open browser and find my class schedule.
- Can you make a sheet for my weekly expenses?
- Open mail and write a short follow-up message.

Risk level:
- Low for interpretation.
- Medium or High based on resulting action type.

### 1) App And System Navigation
What it does:
- Open installed apps (for example: browser, file explorer, notes app, spreadsheet app).
- Open folders and common files.
- Switch focus between open apps.

Example commands:
- Open Chrome.
- Open Downloads folder.
- Switch to Excel.

Risk level:
- Low for opening and switching.
- Medium for modifying system settings.

### 2) Browser Navigation And Web Tasks
What it does:
- Open websites.
- Search the web.
- Navigate pages step by step.
- Fill forms and drafts where allowed.

Example commands:
- Open Gmail and draft a message to Ravi.
- Search for AI automation tutorials.
- Open my sheet and add today expense row.

Risk level:
- Low for browsing/search.
- Medium for form filling/drafting.
- High for irreversible submissions or payments.

### 3) Screen Understanding ("Tell me what is on the screen")
What it does:
- Summarize visible UI context.
- Identify active window/app and likely actionable elements.
- Explain what step to do next.

Example commands:
- What is on my screen right now?
- Where should I click next?
- Summarize this page in 5 points.

Risk level:
- Low for read-only summarization.

MVP constraint:
- Read-only interpretation only.
- No hidden data extraction or background surveillance behavior.

### 4) Message And Writing Tasks
What it does:
- Draft messages, emails, and short replies.
- Rewrite tone (formal, friendly, concise).
- Populate message fields after confirmation.

Example commands:
- Write a polite follow-up email for meeting notes.
- Draft a WhatsApp-style short reminder message.
- Fill subject and body in Gmail draft.

Risk level:
- Medium for writing in user accounts.
- High when sending externally; requires confirmation.

### 5) Spreadsheet And Simple Data Tasks
What it does:
- Create sheet templates (expense, study plan, task tracker).
- Add/update rows and formulas for basic use cases.
- Summarize sheet data in plain language.

Example commands:
- Create a weekly study tracker sheet.
- Add today expense: transport 220.
- Summarize this month total by category.

Risk level:
- Medium for edits.
- High for bulk deletion/overwrite.

### 6) Routine Productivity Actions
What it does:
- Create simple task lists and reminders.
- Organize repeated small workflows.
- Execute multi-step routines with progress updates.

Example commands:
- Create tasks for tomorrow from this note.
- Do my morning setup: open mail, calendar, and to-do list.

Risk level:
- Low to Medium depending on action set.

## Out Of Scope For MVP (Even If Requested)
- Silent autonomous actions without user awareness.
- Financial transactions or irreversible submissions without strict confirmation.
- Running unknown scripts from untrusted sources.
- Full remote-control style operation without policy boundaries.

## Task Execution Contract
For every user task, the agent should:
1. Restate intent briefly.
2. Show plan steps.
3. Ask for confirmation when required by risk policy.
4. Execute step by step.
5. Report completion, failure, or fallback options.

## MVP Starter Task Set (Priority)
Priority P1:
- Voice command handling for core daily tasks.
- Open apps and websites.
- Navigate browser and collect information.
- Draft messages and emails.
- Create/update basic sheets.
- Screen summary and "next step" guidance.

Priority P2:
- Repeatable routines and templates.
- Cross-app task chains with better recovery.

## Acceptance Criteria For This Capability Scope
- At least 20 tasks mapped to capability groups and risk levels.
- Every high-risk task has explicit confirmation rules.
- User can ask "what are you doing now" and receive clear progress state.
- Screen understanding remains read-only and transparent in MVP.
