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
