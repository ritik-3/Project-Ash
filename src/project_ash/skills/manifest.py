from __future__ import annotations

import json
from pathlib import Path

from project_ash.models import SkillManifest


def load_manifest(path: Path) -> SkillManifest:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return SkillManifest.model_validate(data)
