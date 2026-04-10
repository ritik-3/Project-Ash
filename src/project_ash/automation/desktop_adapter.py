from __future__ import annotations

import subprocess


def open_app_with_uia(app: str, label: str | None = None) -> str:
    pretty = label or app

    try:
        from pywinauto import Application

        Application(backend="uia").start(app)
        return f"Opened desktop app with UI Automation: {pretty}"
    except Exception:
        try:
            subprocess.Popen([app], shell=False)
            return f"Opened desktop app with subprocess fallback: {pretty}"
        except FileNotFoundError:
            return f"Could not open app '{app}'. It may not be installed or in PATH."
        except Exception as exc:  # pragma: no cover
            return f"Failed to open app '{app}': {exc}"


def type_in_active_window(text: str) -> str:
    payload = text.strip()
    if not payload:
        return "No text provided to type in active window."

    try:
        from pywinauto.keyboard import send_keys

        escaped = payload.replace("{", "{{}").replace("}", "{}}")
        send_keys(escaped, with_spaces=True, pause=0.01)
        return "Typed text into active window using UI Automation keyboard input."
    except Exception:
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{payload}')"], check=True)
            return "Typed text into active window using Windows SendKeys fallback."
        except Exception:
            return "Failed to type into active window. Ensure a target window is focused."
