from pathlib import Path

from project_ash.automation.browser_adapter import _resolve_playwright_profile_dir
from project_ash.automation.strategies.common import RetryPolicy, retry_call
from project_ash.config import AppConfig


def test_resolve_playwright_profile_dir_creates_folder(tmp_path: Path, monkeypatch) -> None:
    profile_dir = tmp_path / "playwright-profile"

    monkeypatch.setattr(
        "project_ash.automation.browser_adapter.load_default_config",
        lambda: AppConfig(playwright_user_data_dir=profile_dir),
    )

    resolved = _resolve_playwright_profile_dir()
    assert resolved == profile_dir
    assert profile_dir.exists()


def test_retry_call_retries_until_success() -> None:
    state = {"count": 0}

    def flaky() -> str:
        state["count"] += 1
        if state["count"] < 3:
            raise RuntimeError("temporary error")
        return "ok"

    result = retry_call(flaky, RetryPolicy(attempts=3, wait_ms=0))
    assert result == "ok"
    assert state["count"] == 3
