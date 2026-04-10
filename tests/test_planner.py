from project_ash.models import IntentType, ParsedIntent
from project_ash.planner import build_plan


def test_plan_contains_action() -> None:
    parsed = ParsedIntent(
        intent=IntentType.OPEN_APP,
        entities={"app": "chrome", "label": "chrome"},
        confidence=0.9,
        normalized_text="open chrome",
    )
    plan = build_plan("open chrome", parsed)
    assert len(plan.steps) == 1
    assert plan.steps[0].action == "open_app"
