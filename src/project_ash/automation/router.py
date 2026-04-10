from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TargetType(str, Enum):
    BROWSER = "browser"
    DESKTOP = "desktop"
    VISION_FALLBACK = "vision_fallback"


@dataclass
class RouteDecision:
    target: TargetType
    reason: str


def choose_route(action: str, has_dom_target: bool, has_desktop_target: bool) -> RouteDecision:
    if has_dom_target:
        return RouteDecision(
            target=TargetType.BROWSER,
            reason="Browser task detected. Use Playwright DOM control.",
        )

    if has_desktop_target:
        return RouteDecision(
            target=TargetType.DESKTOP,
            reason="Desktop app target detected. Use OS UI automation.",
        )

    return RouteDecision(
        target=TargetType.VISION_FALLBACK,
        reason="No structured target detected. Fallback to screenshot vision pipeline.",
    )
