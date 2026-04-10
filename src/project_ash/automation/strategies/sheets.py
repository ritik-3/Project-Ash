from __future__ import annotations

from project_ash.automation.strategies.common import RetryPolicy

SHEETS_RETRY_POLICY = RetryPolicy(attempts=3, wait_ms=1300)

SHEETS_TITLE_LOCATORS = [
    "input[aria-label='Rename']",
    "input.docs-title-input",
    "div.docs-title-input-label-inner + input",
]

SHEETS_FIRST_CELL_LOCATORS = [
    "div[role='gridcell'][aria-label*='A1']",
    "div.grid-container div[role='gridcell']",
    "div[role='grid'] div[role='gridcell']",
]
