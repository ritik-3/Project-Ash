from __future__ import annotations

from project_ash.models import ExecutionPlan, IntentType, ParsedIntent, PlanStep
from project_ash.risk import classify_risk, requires_confirmation


def build_plan(user_text: str, parsed: ParsedIntent) -> ExecutionPlan:
    risk = classify_risk(parsed)
    ask_confirmation = requires_confirmation(risk)
    lowered = user_text.lower()
    async_cues = ("schedule", "later", "tomorrow", "every ", "remind")
    execution_mode = "async" if any(cue in lowered for cue in async_cues) else "immediate"
    tags = ["scheduled", "async"] if execution_mode == "async" else ["immediate"]

    def _step(action: str, params: dict) -> PlanStep:
        return PlanStep(
            step_id=1,
            action=action,
            params=params,
            risk=risk,
            requires_confirmation=ask_confirmation,
            execution_mode=execution_mode,
            tags=tags,
        )

    if parsed.intent == IntentType.OPEN_APP:
        return ExecutionPlan(user_goal=user_text, steps=[_step("open_app", parsed.entities)])

    if parsed.intent == IntentType.OPEN_WEBSITE:
        return ExecutionPlan(user_goal=user_text, steps=[_step("open_website", parsed.entities)])

    if parsed.intent == IntentType.SEARCH_WEB:
        return ExecutionPlan(user_goal=user_text, steps=[_step("search_web", parsed.entities)])

    if parsed.intent == IntentType.DRAFT_GMAIL:
        return ExecutionPlan(user_goal=user_text, steps=[_step("draft_gmail", parsed.entities)])

    if parsed.intent == IntentType.CREATE_GOOGLE_SHEET:
        return ExecutionPlan(user_goal=user_text, steps=[_step("create_google_sheet", parsed.entities)])

    if parsed.intent == IntentType.ADD_GOOGLE_SHEET_ROW:
        return ExecutionPlan(user_goal=user_text, steps=[_step("add_google_sheet_row", parsed.entities)])

    if parsed.intent == IntentType.TYPE_IN_ACTIVE_WINDOW:
        return ExecutionPlan(user_goal=user_text, steps=[_step("type_in_active_window", parsed.entities)])

    if parsed.intent == IntentType.SCREEN_SUMMARY:
        return ExecutionPlan(user_goal=user_text, steps=[_step("screen_summary", {})])

    if parsed.intent == IntentType.DRAFT_MESSAGE:
        return ExecutionPlan(user_goal=user_text, steps=[_step("draft_message", parsed.entities)])

    if parsed.intent == IntentType.CREATE_SHEET:
        return ExecutionPlan(user_goal=user_text, steps=[_step("create_sheet", parsed.entities)])

    if parsed.intent == IntentType.ADD_SHEET_ROW:
        return ExecutionPlan(user_goal=user_text, steps=[_step("add_sheet_row", parsed.entities)])

    return ExecutionPlan(
        user_goal=user_text,
        steps=[
            PlanStep(
                step_id=1,
                action="ask_clarification",
                params={"question": "I am not sure what action to perform. Please rephrase."},
                risk=risk,
                requires_confirmation=False,
                execution_mode="immediate",
                tags=["clarification"],
            )
        ],
    )
