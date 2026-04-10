from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from project_ash.channels.base import ChannelConnector
from project_ash.models import ChannelEnvelope, ChannelType


class TelegramConnector(ChannelConnector):
    channel_type = ChannelType.TELEGRAM

    def normalize_event(self, payload: dict[str, Any]) -> ChannelEnvelope:
        message = payload.get("message", {})
        chat = message.get("chat", {})
        user = message.get("from", {})
        return ChannelEnvelope(
            envelope_id=str(uuid4()),
            channel_type=self.channel_type,
            channel_user_id=str(user.get("id", "unknown")),
            channel_conversation_id=str(chat.get("id", "unknown")),
            timestamp_utc=datetime.now(timezone.utc),
            message_text=str(message.get("text", "")),
            attachments=[],
            metadata={"raw_provider": "telegram"},
        )

    def format_outbound(self, conversation_id: str, text: str) -> dict[str, Any]:
        return {"chat_id": conversation_id, "text": text}
