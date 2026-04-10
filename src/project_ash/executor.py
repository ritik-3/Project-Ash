from __future__ import annotations

from project_ash.models import StepResult
from project_ash.skills.desktop import open_app, open_website, search_web
from project_ash.skills.productivity import add_sheet_row, create_sheet, draft_message
from project_ash.skills.screen import summarize_screen


def run_action(step_id: int, action: str, params: dict) -> StepResult:
    if action == "open_app":
        message = open_app(params.get("app", ""), params.get("label"))
        return StepResult(step_id=step_id, success=True, message=message)

    if action == "open_website":
        message = open_website(params.get("url", ""))
        return StepResult(step_id=step_id, success=True, message=message)

    if action == "search_web":
        message = search_web(params.get("query", ""))
        return StepResult(step_id=step_id, success=True, message=message)

    if action == "screen_summary":
        message = summarize_screen()
        return StepResult(step_id=step_id, success=True, message=message)

    if action == "draft_message":
        message = draft_message(params.get("prompt", ""))
        return StepResult(step_id=step_id, success=True, message=message)

    if action == "create_sheet":
        message = create_sheet(params.get("title", "Untitled Sheet"))
        return StepResult(step_id=step_id, success=True, message=message)

    if action == "add_sheet_row":
        message = add_sheet_row(params.get("raw", ""))
        return StepResult(step_id=step_id, success=True, message=message)

    if action == "ask_clarification":
        return StepResult(
            step_id=step_id,
            success=False,
            message=params.get("question", "Please clarify your request."),
        )

    return StepResult(step_id=step_id, success=False, message=f"Unknown action: {action}")
