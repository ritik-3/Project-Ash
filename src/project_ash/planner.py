from __future__ import annotations

from project_ash.models import ExecutionPlan, IntentType, ParsedIntent, PlanStep
from project_ash.risk import classify_risk, requires_confirmation


def build_plan(user_text: str, parsed: ParsedIntent) -> ExecutionPlan:
    risk = classify_risk(parsed)
    ask_confirmation = requires_confirmation(risk)

    if parsed.intent == IntentType.OPEN_APP:
        return ExecutionPlan(
            user_goal=user_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="open_app",
                    params=parsed.entities,
                    risk=risk,
                    requires_confirmation=ask_confirmation,
                )
            ],
        )

    if parsed.intent == IntentType.OPEN_WEBSITE:
        return ExecutionPlan(
            user_goal=user_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="open_website",
                    params=parsed.entities,
                    risk=risk,
                    requires_confirmation=ask_confirmation,
                )
            ],
        )

    if parsed.intent == IntentType.SEARCH_WEB:
        return ExecutionPlan(
            user_goal=user_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="search_web",
                    params=parsed.entities,
                    risk=risk,
                    requires_confirmation=ask_confirmation,
                )
            ],
        )

    if parsed.intent == IntentType.SCREEN_SUMMARY:
        return ExecutionPlan(
            user_goal=user_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="screen_summary",
                    params={},
                    risk=risk,
                    requires_confirmation=ask_confirmation,
                )
            ],
        )

    if parsed.intent == IntentType.DRAFT_MESSAGE:
        return ExecutionPlan(
            user_goal=user_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="draft_message",
                    params=parsed.entities,
                    risk=risk,
                    requires_confirmation=ask_confirmation,
                )
            ],
        )

    if parsed.intent == IntentType.CREATE_SHEET:
        return ExecutionPlan(
            user_goal=user_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="create_sheet",
                    params=parsed.entities,
                    risk=risk,
                    requires_confirmation=ask_confirmation,
                )
            ],
        )

    if parsed.intent == IntentType.ADD_SHEET_ROW:
        return ExecutionPlan(
            user_goal=user_text,
            steps=[
                PlanStep(
                    step_id=1,
                    action="add_sheet_row",
                    params=parsed.entities,
                    risk=risk,
                    requires_confirmation=ask_confirmation,
                )
            ],
        )

    return ExecutionPlan(
        user_goal=user_text,
        steps=[
            PlanStep(
                step_id=1,
                action="ask_clarification",
                params={"question": "I am not sure what action to perform. Please rephrase."},
                risk=risk,
                requires_confirmation=False,
            )
        ],
    )
