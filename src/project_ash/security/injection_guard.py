from __future__ import annotations

import re


class InjectionGuard:
    _PATTERNS = [
        re.compile(r"(?i)ignore\s+all\s+previous\s+instructions"),
        re.compile(r"(?i)reveal\s+(system|developer)\s+prompt"),
        re.compile(r"(?i)run\s+shell\s+command\s+without\s+confirmation"),
    ]

    def is_suspicious(self, text: str) -> bool:
        return any(p.search(text) for p in self._PATTERNS)
