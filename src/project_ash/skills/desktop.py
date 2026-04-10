from __future__ import annotations

import subprocess
import webbrowser


def open_app(app: str, label: str | None = None) -> str:
    try:
        subprocess.Popen([app], shell=False)
        pretty = label or app
        return f"Opened app: {pretty}"
    except FileNotFoundError:
        return f"Could not open app '{app}'. It may not be installed or in PATH."
    except Exception as exc:  # pragma: no cover
        return f"Failed to open app '{app}': {exc}"


def open_website(url: str) -> str:
    target = url if url.startswith("http") else f"https://{url}"
    webbrowser.open(target)
    return f"Opened website: {target}"


def search_web(query: str) -> str:
    cleaned = query.strip() or ""
    target = f"https://www.google.com/search?q={cleaned.replace(' ', '+')}"
    webbrowser.open(target)
    return f"Searching web for: {cleaned or 'your request'}"
