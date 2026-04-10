from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from project_ash.channels.base import ChannelConnector
from project_ash.models import ChannelEnvelope, ChannelType


class WhatsAppConnector(ChannelConnector):
    channel_type = ChannelType.WHATSAPP

    def normalize_event(self, payload: dict) -> ChannelEnvelope:
        return ChannelEnvelope(
            envelope_id=str(uuid4()),
            channel_type=self.channel_type,
            channel_user_id=str(payload.get("from", "unknown")),
            channel_conversation_id=str(payload.get("conversation_id", "unknown")),
            timestamp_utc=datetime.now(timezone.utc),
            message_text=str(payload.get("text", "")),
            attachments=[],
            metadata={"raw_provider": "whatsapp"},
        )

    def format_outbound(self, conversation_id: str, text: str) -> dict[str, str]:
        return {"to": conversation_id, "text": text}
