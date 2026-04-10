from __future__ import annotations

from project_ash.models import IntentType, ParsedIntent, RiskLevel


def classify_risk(parsed: ParsedIntent) -> RiskLevel:
    if parsed.intent in {IntentType.SCREEN_SUMMARY, IntentType.SEARCH_WEB, IntentType.OPEN_WEBSITE, IntentType.OPEN_APP}:
        return RiskLevel.LOW

    if parsed.intent in {IntentType.DRAFT_MESSAGE, IntentType.CREATE_SHEET, IntentType.ADD_SHEET_ROW}:
        return RiskLevel.MEDIUM

    return RiskLevel.HIGH


def requires_confirmation(risk: RiskLevel) -> bool:
    return risk in {RiskLevel.MEDIUM, RiskLevel.HIGH}
