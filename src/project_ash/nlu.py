from __future__ import annotations

import re

from project_ash.models import IntentType, ParsedIntent


APP_KEYWORDS = {
    "chrome": "chrome",
    "edge": "msedge",
    "notepad": "notepad",
    "excel": "excel",
    "word": "winword",
    "explorer": "explorer",
}


def normalize_text(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def parse_intent(text: str) -> ParsedIntent:
    normalized = normalize_text(text)

    if any(token in normalized for token in ["what is on my screen", "screen", "on screen"]):
        return ParsedIntent(
            intent=IntentType.SCREEN_SUMMARY,
            confidence=0.8,
            normalized_text=normalized,
        )

    if "search" in normalized or "find" in normalized:
        query = normalized.replace("search", "").replace("find", "").strip()
        return ParsedIntent(
            intent=IntentType.SEARCH_WEB,
            entities={"query": query},
            confidence=0.85,
            normalized_text=normalized,
        )

    if any(word in normalized for word in ["open", "launch", "start"]):
        for key, app in APP_KEYWORDS.items():
            if key in normalized:
                return ParsedIntent(
                    intent=IntentType.OPEN_APP,
                    entities={"app": app, "label": key},
                    confidence=0.9,
                    normalized_text=normalized,
                )

        url_match = re.search(r"(https?://\S+|\b[a-z0-9-]+\.(com|org|net|in)\b)", normalized)
        if url_match:
            return ParsedIntent(
                intent=IntentType.OPEN_WEBSITE,
                entities={"url": url_match.group(1)},
                confidence=0.88,
                normalized_text=normalized,
            )

    if any(token in normalized for token in ["draft", "write message", "write mail", "email"]):
        return ParsedIntent(
            intent=IntentType.DRAFT_MESSAGE,
            entities={"prompt": text.strip()},
            confidence=0.82,
            normalized_text=normalized,
        )

    if any(token in normalized for token in ["create sheet", "new sheet"]):
        return ParsedIntent(
            intent=IntentType.CREATE_SHEET,
            entities={"title": "Untitled Sheet"},
            confidence=0.75,
            normalized_text=normalized,
        )

    if "add" in normalized and "sheet" in normalized:
        return ParsedIntent(
            intent=IntentType.ADD_SHEET_ROW,
            entities={"raw": text.strip()},
            confidence=0.72,
            normalized_text=normalized,
        )

    return ParsedIntent(
        intent=IntentType.UNKNOWN,
        confidence=0.3,
        normalized_text=normalized,
    )
