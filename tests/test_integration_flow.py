from pathlib import Path

from project_ash.models import InputMode, UserInput
from project_ash.orchestrator import AssistantOrchestrator


def test_voice_to_plan_route_and_sqlite_log(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "ash_memory.db"
    orchestrator = AssistantOrchestrator(log_dir=tmp_path, sqlite_db_path=db_path)

    # Avoid launching an actual browser in test runs.
    monkeypatch.setattr(
        "project_ash.executor.open_website_with_playwright",
        lambda url: f"Opened website with Playwright: {url}",
    )

    user_input = UserInput(mode=InputMode.VOICE, text="open github.com")
    plan = orchestrator.create_plan(user_input)
    result = orchestrator.execute_plan(plan, confirmed=True)

    assert result.success is True
    assert len(result.step_results) == 1
    assert result.step_results[0].data["route"] == "browser"

    history_rows = orchestrator.get_history("github", limit=5)
    assert len(history_rows) >= 1
    assert "open github.com" in history_rows[0]["goal"]


def test_confirmation_gate_for_medium_risk(tmp_path: Path) -> None:
    db_path = tmp_path / "ash_memory.db"
    orchestrator = AssistantOrchestrator(log_dir=tmp_path, sqlite_db_path=db_path)

    plan = orchestrator.create_plan(UserInput(mode=InputMode.TEXT, text="draft a follow up email"))
    blocked_result = orchestrator.execute_plan(plan, confirmed=False)
    allowed_result = orchestrator.execute_plan(plan, confirmed=True)

    assert blocked_result.success is False
    assert "Confirmation required" in blocked_result.summary
    assert allowed_result.success is True


def test_gmail_draft_route(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "ash_memory.db"
    orchestrator = AssistantOrchestrator(log_dir=tmp_path, sqlite_db_path=db_path)

    monkeypatch.setattr(
        "project_ash.executor.draft_gmail_with_playwright",
        lambda prompt, to=None: "Opened Gmail draft compose window with pre-filled content.",
    )

    plan = orchestrator.create_plan(UserInput(mode=InputMode.TEXT, text="draft email to foo@example.com"))
    result = orchestrator.execute_plan(plan, confirmed=True)

    assert result.success is True
    assert result.step_results[0].data["route"] == "browser"


def test_type_in_active_window_flow(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "ash_memory.db"
    orchestrator = AssistantOrchestrator(log_dir=tmp_path, sqlite_db_path=db_path)

    monkeypatch.setattr(
        "project_ash.executor.type_in_active_window",
        lambda text: "Typed text into active window using UI Automation keyboard input.",
    )

    plan = orchestrator.create_plan(UserInput(mode=InputMode.TEXT, text="type this hello world"))
    blocked = orchestrator.execute_plan(plan, confirmed=False)
    allowed = orchestrator.execute_plan(plan, confirmed=True)

    assert blocked.success is False
    assert allowed.success is True
    assert allowed.step_results[0].data["route"] == "desktop"
