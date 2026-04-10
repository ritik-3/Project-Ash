from __future__ import annotations

import re

_SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|password)\s*[:=]\s*\S+")


def sanitize_text(text: str) -> str:
    return _SECRET_RE.sub("[REDACTED_SECRET]", text)
