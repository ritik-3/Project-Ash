from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import RLock

from app.schemas.chat import ChatMessage


@dataclass(slots=True)
class ConversationTurn:
    user: str
    assistant: str


class SessionMemoryService:
    def __init__(self, limit: int = 8) -> None:
        self.limit = limit
        self._sessions: dict[str, deque[ConversationTurn]] = defaultdict(lambda: deque(maxlen=self.limit))
        self._lock = RLock()

    def append_turn(self, session_id: str, user_message: str, assistant_message: str) -> int:
        with self._lock:
            self._sessions[session_id].append(ConversationTurn(user=user_message, assistant=assistant_message))
            return len(self._sessions[session_id])

    def recent_turns(self, session_id: str) -> list[ConversationTurn]:
        with self._lock:
            return list(self._sessions[session_id])

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def to_messages(self, session_id: str) -> list[ChatMessage]:
        turns = self.recent_turns(session_id)
        messages: list[ChatMessage] = []
        for turn in turns:
            messages.append(ChatMessage(role="user", content=turn.user))
            messages.append(ChatMessage(role="assistant", content=turn.assistant))
        return messages

    def history_size(self, session_id: str) -> int:
        with self._lock:
            return len(self._sessions[session_id])