from __future__ import annotations

from typing import Any

from project_ash.channels.base import ChannelConnector
from project_ash.channels.discord import DiscordConnector
from project_ash.channels.slack import SlackConnector
from project_ash.channels.telegram import TelegramConnector
from project_ash.channels.whatsapp import WhatsAppConnector
from project_ash.models import ChannelEnvelope, ChannelType


class ChannelRouter:
    def __init__(self) -> None:
        self._connectors: dict[str, ChannelConnector] = {
            ChannelType.TELEGRAM.value: TelegramConnector(),
            ChannelType.SLACK.value: SlackConnector(),
            ChannelType.DISCORD.value: DiscordConnector(),
            ChannelType.WHATSAPP.value: WhatsAppConnector(),
        }

    def normalize(self, provider: str, payload: dict[str, Any]) -> ChannelEnvelope:
        connector = self._connectors.get(provider)
        if connector is None:
            raise ValueError(f"Unsupported channel provider: {provider}")
        return connector.normalize_event(payload)

    def prepare_outbound(self, provider: str, conversation_id: str, text: str) -> dict[str, Any]:
        connector = self._connectors.get(provider)
        if connector is None:
            raise ValueError(f"Unsupported channel provider: {provider}")
        return connector.format_outbound(conversation_id, text)
