from __future__ import annotations

from project_ash.automation.strategies.common import RetryPolicy

GMAIL_RETRY_POLICY = RetryPolicy(attempts=3, wait_ms=1200)

GMAIL_COMPOSE_BUTTON_LOCATORS = [
    "div[gh='cm']",
    "div[role='button'][aria-label*='Compose']",
    "div[role='button'][data-tooltip='Compose']",
]

GMAIL_TO_FIELD_LOCATORS = [
    "textarea[name='to']",
    "input[aria-label='To recipients']",
    "div[aria-label='To recipients'] input",
]

GMAIL_SUBJECT_LOCATORS = [
    "input[name='subjectbox']",
    "input[aria-label='Subject']",
]

GMAIL_BODY_LOCATORS = [
    "div[aria-label='Message Body']",
    "div[role='textbox'][aria-label='Message Body']",
]
