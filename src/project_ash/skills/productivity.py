from __future__ import annotations

from datetime import datetime


def draft_message(prompt: str) -> str:
    # Placeholder draft engine for MVP foundation.
    return (
        "Draft created:\n"
        f"Subject: Quick Follow-up ({datetime.now().date().isoformat()})\n"
        f"Body: {prompt}\n"
    )


def create_sheet(title: str) -> str:
    return f"Sheet template prepared with title: {title}"


def add_sheet_row(raw: str) -> str:
    return f"Captured sheet row request: {raw}"
