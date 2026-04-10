from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from project_ash.config import AppConfig, load_default_config


@dataclass(frozen=True)
class DiagnosticResult:
    name: str
    status: str
    message: str


def check_ollama(cfg: AppConfig) -> DiagnosticResult:
    try:
        proc = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return DiagnosticResult("ollama", "fail", "Ollama CLI not ready.")
        if cfg.ollama_model in proc.stdout:
            return DiagnosticResult("ollama", "pass", f"Model available: {cfg.ollama_model}")
        return DiagnosticResult("ollama", "warn", f"Ollama reachable, model missing: {cfg.ollama_model}")
    except FileNotFoundError:
        return DiagnosticResult("ollama", "fail", "Ollama not installed.")


def check_whisper(cfg: AppConfig) -> DiagnosticResult:
    try:
        import faster_whisper  # noqa: F401

        return DiagnosticResult(
            "faster_whisper",
            "pass",
            f"faster-whisper import OK (device target: {cfg.faster_whisper_device}).",
        )
    except Exception as exc:
        return DiagnosticResult("faster_whisper", "fail", f"faster-whisper unavailable: {exc}")


def check_piper(cfg: AppConfig) -> DiagnosticResult:
    piper_path = Path(cfg.piper_exe)
    piper_ok = piper_path.exists() or shutil.which(cfg.piper_exe) is not None
    if not piper_ok:
        return DiagnosticResult("piper", "fail", f"Piper executable not found: {cfg.piper_exe}")

    if not cfg.piper_model_path:
        return DiagnosticResult("piper", "warn", "Piper available but model path is not configured.")

    model_path = Path(cfg.piper_model_path)
    if not model_path.exists():
        return DiagnosticResult("piper", "fail", f"Piper model not found: {cfg.piper_model_path}")

    return DiagnosticResult("piper", "pass", "Piper executable and model path are valid.")


def check_playwright_install(cfg: AppConfig) -> DiagnosticResult:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            path = p.chromium.executable_path
            if path and Path(path).exists():
                return DiagnosticResult("playwright", "pass", "Playwright browser runtime is installed.")
            return DiagnosticResult("playwright", "warn", "Playwright imported but browser runtime path unresolved.")
    except Exception as exc:
        return DiagnosticResult("playwright", "fail", f"Playwright unavailable: {exc}")


def check_automation_permissions(cfg: AppConfig) -> DiagnosticResult:
    try:
        import ctypes

        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return DiagnosticResult("automation_permissions", "warn", "No foreground window detected.")

        import pywinauto  # noqa: F401

        return DiagnosticResult("automation_permissions", "pass", "Desktop automation import and foreground access OK.")
    except Exception as exc:
        return DiagnosticResult("automation_permissions", "fail", f"Automation dependency/permission issue: {exc}")


def run_diagnostics(cfg: AppConfig | None = None) -> list[DiagnosticResult]:
    config = cfg or load_default_config()
    checks: list[Callable[[AppConfig], DiagnosticResult]] = [
        check_ollama,
        check_whisper,
        check_piper,
        check_playwright_install,
        check_automation_permissions,
    ]
    return [check(config) for check in checks]


def _print_report(results: list[DiagnosticResult]) -> None:
    print("Project Ash Diagnostics")
    print("=" * 24)
    for result in results:
        print(f"- {result.name}: {result.status.upper()} - {result.message}")


def main() -> int:
    results = run_diagnostics()
    _print_report(results)

    has_fail = any(r.status == "fail" for r in results)
    return 1 if has_fail else 0
