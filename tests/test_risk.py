from project_ash.models import IntentType, ParsedIntent, RiskLevel
from project_ash.risk import classify_risk, requires_confirmation


def test_low_risk_intent() -> None:
    parsed = ParsedIntent(intent=IntentType.OPEN_WEBSITE, normalized_text="open site", confidence=0.9)
    assert classify_risk(parsed) == RiskLevel.LOW
    assert requires_confirmation(RiskLevel.LOW) is False


def test_medium_risk_intent() -> None:
    parsed = ParsedIntent(intent=IntentType.DRAFT_MESSAGE, normalized_text="draft", confidence=0.8)
    assert classify_risk(parsed) == RiskLevel.MEDIUM
    assert requires_confirmation(RiskLevel.MEDIUM) is True
