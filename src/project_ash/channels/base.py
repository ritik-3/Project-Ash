from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from project_ash.models import ChannelEnvelope, ChannelType


class ChannelConnector(ABC):
    channel_type: ChannelType

    @abstractmethod
    def normalize_event(self, payload: dict[str, Any]) -> ChannelEnvelope:
        raise NotImplementedError

    @abstractmethod
    def format_outbound(self, conversation_id: str, text: str) -> dict[str, Any]:
        raise NotImplementedError
