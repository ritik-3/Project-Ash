from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from project_ash.channels.base import ChannelConnector
from project_ash.models import ChannelEnvelope, ChannelType


class SlackConnector(ChannelConnector):
    channel_type = ChannelType.SLACK

    def normalize_event(self, payload: dict[str, Any]) -> ChannelEnvelope:
        event = payload.get("event", {})
        return ChannelEnvelope(
            envelope_id=str(uuid4()),
            channel_type=self.channel_type,
            channel_user_id=str(event.get("user", "unknown")),
            channel_conversation_id=str(event.get("channel", "unknown")),
            timestamp_utc=datetime.now(timezone.utc),
            message_text=str(event.get("text", "")),
            attachments=[],
            metadata={"raw_provider": "slack"},
        )

    def format_outbound(self, conversation_id: str, text: str) -> dict[str, Any]:
        return {"channel": conversation_id, "text": text}
