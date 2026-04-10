from __future__ import annotations

from project_ash.models import IntentType, ParsedIntent, RiskLevel


def classify_risk(parsed: ParsedIntent, autonomous_mode: bool = False) -> RiskLevel:
    if autonomous_mode and parsed.intent in {
        IntentType.DRAFT_MESSAGE,
        IntentType.CREATE_SHEET,
        IntentType.ADD_SHEET_ROW,
        IntentType.DRAFT_GMAIL,
        IntentType.CREATE_GOOGLE_SHEET,
        IntentType.ADD_GOOGLE_SHEET_ROW,
        IntentType.TYPE_IN_ACTIVE_WINDOW,
    }:
        return RiskLevel.HIGH

    if parsed.intent in {IntentType.SCREEN_SUMMARY, IntentType.SEARCH_WEB, IntentType.OPEN_WEBSITE, IntentType.OPEN_APP}:
        return RiskLevel.LOW

    if parsed.intent in {
        IntentType.DRAFT_MESSAGE,
        IntentType.CREATE_SHEET,
        IntentType.ADD_SHEET_ROW,
        IntentType.DRAFT_GMAIL,
        IntentType.CREATE_GOOGLE_SHEET,
        IntentType.ADD_GOOGLE_SHEET_ROW,
        IntentType.TYPE_IN_ACTIVE_WINDOW,
    }:
        return RiskLevel.MEDIUM

    return RiskLevel.HIGH


def requires_confirmation(risk: RiskLevel) -> bool:
    return risk in {RiskLevel.MEDIUM, RiskLevel.HIGH}
