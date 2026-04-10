import json

from project_ash.models import PlanStep, RiskLevel
from project_ash.skills.manifest import load_manifest
from project_ash.skills.policy import PolicyGuard


def test_manifest_load_and_policy(tmp_path) -> None:
    manifest_path = tmp_path / "skill.json"
    manifest_path.write_text(
        json.dumps(
            {
                "name": "demo-skill",
                "version": "1.0.0",
                "description": "Demo",
                "actions_exposed": ["search_web"],
                "required_permissions": ["web.read"],
                "risk_level_default": "medium",
                "external_scopes": [],
                "network_policy": "allowlist",
                "requires_confirmation": True,
            }
        ),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)
    assert manifest.name == "demo-skill"

    guard = PolicyGuard()
    step = PlanStep(step_id=1, action="danger", risk=RiskLevel.HIGH, requires_confirmation=False)
    decision = guard.check_step(step)
    assert decision.allowed is False
