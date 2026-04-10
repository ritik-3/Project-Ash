from __future__ import annotations

from typing import Any

from project_ash.automation.browser_adapter import (
    add_google_sheet_row_with_playwright,
    create_google_sheet_with_playwright,
    draft_gmail_with_playwright,
    open_website_with_playwright,
    search_web_with_playwright,
)
from project_ash.automation.desktop_adapter import open_app_with_uia, type_in_active_window
from project_ash.automation.router import choose_route
from project_ash.automation.vision_adapter import summarize_screen_with_ocr
from project_ash.models import PlanStep, StepResult
from project_ash.skills.policy import PolicyGuard
from project_ash.skills.productivity import add_sheet_row, create_sheet, draft_message


def run_action(
    step_id: int,
    action: str,
    params: dict[str, Any],
    step: PlanStep | None = None,
    policy_guard: PolicyGuard | None = None,
) -> StepResult:
    if step is not None and policy_guard is not None:
        decision = policy_guard.check_step(step)
        if not decision.allowed:
            return StepResult(step_id=step_id, success=False, message=f"Policy blocked action: {decision.reason}")

    if action == "open_app":
        route = choose_route(action=action, has_dom_target=False, has_desktop_target=True)
        message = open_app_with_uia(params.get("app", ""), params.get("label"))
        return StepResult(
            step_id=step_id,
            success=True,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

    if action == "open_website":
        route = choose_route(action=action, has_dom_target=True, has_desktop_target=False)
        message = open_website_with_playwright(params.get("url", ""))
        return StepResult(
            step_id=step_id,
            success=True,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

    if action == "search_web":
        route = choose_route(action=action, has_dom_target=True, has_desktop_target=False)
        message = search_web_with_playwright(params.get("query", ""))
        return StepResult(
            step_id=step_id,
            success=True,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

    if action == "screen_summary":
        route = choose_route(action=action, has_dom_target=False, has_desktop_target=False)
        message = summarize_screen_with_ocr()
        return StepResult(
            step_id=step_id,
            success=True,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

    if action == "draft_gmail":
        route = choose_route(action=action, has_dom_target=True, has_desktop_target=False)
        message = draft_gmail_with_playwright(params.get("prompt", ""), params.get("to"))
        return StepResult(
            step_id=step_id,
            success=True,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

    if action == "create_google_sheet":
        route = choose_route(action=action, has_dom_target=True, has_desktop_target=False)
        message = create_google_sheet_with_playwright(params.get("title", "Untitled Sheet"))
        return StepResult(
            step_id=step_id,
            success=True,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

    if action == "add_google_sheet_row":
        route = choose_route(action=action, has_dom_target=True, has_desktop_target=False)
        message = add_google_sheet_row_with_playwright(params.get("row_text", ""))
        return StepResult(
            step_id=step_id,
            success=True,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

    if action == "type_in_active_window":
        route = choose_route(action=action, has_dom_target=False, has_desktop_target=True)
        message = type_in_active_window(params.get("text", ""))
        return StepResult(
            step_id=step_id,
            success="Failed" not in message,
            message=message,
            data={"route": route.target.value, "reason": route.reason},
        )

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
