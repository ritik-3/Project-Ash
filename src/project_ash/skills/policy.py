from __future__ import annotations

from project_ash.models import PlanStep, PolicyDecision, RiskLevel


class PolicyGuard:
    def check_step(self, step: PlanStep) -> PolicyDecision:
        if step.risk == RiskLevel.HIGH and not step.requires_confirmation:
            return PolicyDecision(allowed=False, reason="High-risk action must require confirmation.")
        return PolicyDecision(allowed=True, reason="Allowed by default policy.")
