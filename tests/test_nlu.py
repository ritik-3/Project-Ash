from project_ash.models import IntentType
from project_ash.nlu import parse_intent


def test_parse_open_app() -> None:
    parsed = parse_intent("open chrome")
    assert parsed.intent == IntentType.OPEN_APP
    assert parsed.entities["app"] == "chrome"


def test_parse_open_website() -> None:
    parsed = parse_intent("open github.com")
    assert parsed.intent == IntentType.OPEN_WEBSITE


def test_parse_screen_summary() -> None:
    parsed = parse_intent("what is on my screen")
    assert parsed.intent == IntentType.SCREEN_SUMMARY


def test_parse_gmail_draft_intent() -> None:
    parsed = parse_intent("draft email to test@example.com about project update")
    assert parsed.intent == IntentType.DRAFT_GMAIL
    assert parsed.entities.get("to") == "test@example.com"


def test_parse_google_sheet_row_intent() -> None:
    parsed = parse_intent("add row date today, transport 220 to google sheet")
    assert parsed.intent == IntentType.ADD_GOOGLE_SHEET_ROW


def test_parse_type_in_active_window() -> None:
    parsed = parse_intent("type this hello from ash")
    assert parsed.intent == IntentType.TYPE_IN_ACTIVE_WINDOW
