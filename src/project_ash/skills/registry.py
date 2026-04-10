from __future__ import annotations

from pathlib import Path

from project_ash.memory.sqlite_store import SQLiteMemoryStore
from project_ash.models import SkillManifest
from project_ash.skills.manifest import load_manifest


class SkillRegistry:
    def __init__(self, store: SQLiteMemoryStore) -> None:
        self.store = store

    def install_from_file(self, path: Path) -> SkillManifest:
        manifest = load_manifest(path)
        self.store.upsert_skill(manifest, enabled=True)
        return manifest

    def list_skills(self) -> list[dict[str, object]]:
        return self.store.list_skills()

    def set_enabled(self, name: str, enabled: bool) -> bool:
        return self.store.set_skill_enabled(name, enabled)

    def get_manifest(self, name: str) -> SkillManifest | None:
        data = self.store.get_skill(name)
        if not data:
            return None
        return SkillManifest.model_validate(data)
