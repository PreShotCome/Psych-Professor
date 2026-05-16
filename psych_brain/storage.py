"""
JSON-based persistence layer for user profiles.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .models import UserProfile


class ProfileStorage:
    def __init__(self, profiles_dir: str = "profiles"):
        self.dir = Path(profiles_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in user_id)
        return self.dir / f"{safe}.json"

    def load(self, user_id: str) -> UserProfile | None:
        p = self._path(user_id)
        if not p.exists():
            return None
        with open(p) as f:
            return UserProfile.from_dict(json.load(f))

    def save(self, profile: UserProfile) -> None:
        p = self._path(profile.user_id)
        with open(p, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)

    def list_users(self) -> list[str]:
        return [f.stem for f in self.dir.glob("*.json")]

    def exists(self, user_id: str) -> bool:
        return self._path(user_id).exists()
