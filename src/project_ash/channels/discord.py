from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from project_ash.channels.base import ChannelConnector
from project_ash.models import ChannelEnvelope, ChannelType


class DiscordConnector(ChannelConnector):
    channel_type = ChannelType.DISCORD

    def normalize_event(self, payload: dict) -> ChannelEnvelope:
        author = payload.get("author", {})
        return ChannelEnvelope(
            envelope_id=str(uuid4()),
            channel_type=self.channel_type,
            channel_user_id=str(author.get("id", "unknown")),
            channel_conversation_id=str(payload.get("channel_id", "unknown")),
            timestamp_utc=datetime.now(timezone.utc),
            message_text=str(payload.get("content", "")),
            attachments=[],
            metadata={"raw_provider": "discord"},
        )

    def format_outbound(self, conversation_id: str, text: str) -> dict[str, str]:
        return {"channel_id": conversation_id, "content": text}
