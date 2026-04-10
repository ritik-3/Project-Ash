from __future__ import annotations

import os


class SecretManager:
    def get(self, key: str, default: str | None = None) -> str | None:
        return os.environ.get(key, default)
