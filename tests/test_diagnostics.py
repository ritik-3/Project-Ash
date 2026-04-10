from project_ash.config import AppConfig
from project_ash.diagnostics import DiagnosticResult, run_diagnostics


def test_run_diagnostics_aggregates_checks(monkeypatch) -> None:
    cfg = AppConfig()

    monkeypatch.setattr(
        "project_ash.diagnostics.check_ollama",
        lambda _cfg: DiagnosticResult("ollama", "pass", "ok"),
    )
    monkeypatch.setattr(
        "project_ash.diagnostics.check_whisper",
        lambda _cfg: DiagnosticResult("faster_whisper", "warn", "missing"),
    )
    monkeypatch.setattr(
        "project_ash.diagnostics.check_piper",
        lambda _cfg: DiagnosticResult("piper", "pass", "ok"),
    )
    monkeypatch.setattr(
        "project_ash.diagnostics.check_playwright_install",
        lambda _cfg: DiagnosticResult("playwright", "pass", "ok"),
    )
    monkeypatch.setattr(
        "project_ash.diagnostics.check_automation_permissions",
        lambda _cfg: DiagnosticResult("automation_permissions", "pass", "ok"),
    )

    report = run_diagnostics(cfg)
    assert len(report) == 5
    assert {item.name for item in report} == {
        "ollama",
        "faster_whisper",
        "piper",
        "playwright",
        "automation_permissions",
    }
