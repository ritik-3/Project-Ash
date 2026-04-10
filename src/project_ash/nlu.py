from __future__ import annotations

import json
import re
from typing import Any

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

    if any(token in normalized for token in ["type ", "write in app", "type this"]) and "email" not in normalized:
        payload = text.strip()
        for marker in ["type ", "type this ", "write in app "]:
            if normalized.startswith(marker):
                payload = text[len(marker) :].strip()
                break
        return ParsedIntent(
            intent=IntentType.TYPE_IN_ACTIVE_WINDOW,
            entities={"text": payload},
            confidence=0.8,
            normalized_text=normalized,
        )

    if any(token in normalized for token in ["gmail", "email draft", "draft mail", "draft email"]):
        entities: dict[str, str] = {"prompt": text.strip()}
        to_match = re.search(r"to\s+([a-zA-Z0-9_.@+-]+)", text)
        if to_match:
            entities["to"] = to_match.group(1)
        return ParsedIntent(
            intent=IntentType.DRAFT_GMAIL,
            entities=entities,
            confidence=0.84,
            normalized_text=normalized,
        )

    if any(token in normalized for token in ["google sheet", "spreadsheet"]) and any(
        token in normalized for token in ["create", "new"]
    ):
        title = "Untitled Sheet"
        title_match = re.search(r"(?:called|named|title)\s+(.+)$", text, flags=re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        return ParsedIntent(
            intent=IntentType.CREATE_GOOGLE_SHEET,
            entities={"title": title},
            confidence=0.8,
            normalized_text=normalized,
        )

    if any(token in normalized for token in ["google sheet", "spreadsheet", "sheet"]) and any(
        token in normalized for token in ["add row", "insert row", "add to sheet"]
    ):
        row_text = text.strip()
        row_match = re.search(r"(?:add row|insert row|add to sheet)[:\s]+(.+)$", text, flags=re.IGNORECASE)
        if row_match:
            row_text = row_match.group(1).strip()
        return ParsedIntent(
            intent=IntentType.ADD_GOOGLE_SHEET_ROW,
            entities={"row_text": row_text},
            confidence=0.78,
            normalized_text=normalized,
        )

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


def parse_intent_with_ollama(text: str, llm_client: Any) -> ParsedIntent | None:
    normalized = normalize_text(text)
    prompt = (
        "Classify this user command into one intent and entities. "
        "Return only compact JSON with keys: intent, entities, confidence. "
        "Allowed intents: open_app, open_website, screen_summary, draft_message, "
        "create_sheet, add_sheet_row, search_web, unknown. "
        f"User command: {text}"
    )

    response = llm_client.generate(prompt, temperature=0.0)
    raw = response.text.strip()
    if not raw or "unavailable" in raw.lower():
        return None

    json_match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not json_match:
        return None

    try:
        payload = json.loads(json_match.group(0))
        intent_name = str(payload.get("intent", "unknown")).lower().strip()
        intent = IntentType(intent_name) if intent_name in {i.value for i in IntentType} else IntentType.UNKNOWN
        entities = payload.get("entities") if isinstance(payload.get("entities"), dict) else {}
        confidence = float(payload.get("confidence", 0.65))

        return ParsedIntent(
            intent=intent,
            entities=entities,
            confidence=max(0.0, min(confidence, 1.0)),
            normalized_text=normalized,
        )
    except (ValueError, json.JSONDecodeError, TypeError):
        return None
