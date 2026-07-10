"""
PlacementPilot AI — Student Profile Manager
Stores profiles as JSON files in the profiles/ directory.
"""
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
PROFILES_DIR = Path("profiles")


class ProfileManager:
    def __init__(self):
        PROFILES_DIR.mkdir(exist_ok=True)

    def _path(self, profile_id: str) -> Path:
        safe_id = "".join(c for c in profile_id if c.isalnum() or c in "-_")
        return PROFILES_DIR / f"{safe_id}.json"

    def save_profile(self, profile_id: str, data: dict):
        try:
            path = self._path(profile_id)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Profile saved: %s", profile_id)
        except OSError as exc:
            logger.error("Failed to save profile %s: %s", profile_id, exc)

    def load_profile(self, profile_id: str) -> dict:
        path = self._path(profile_id)
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to load profile %s: %s", profile_id, exc)
            return {}

    def list_profiles(self) -> list:
        profiles = []
        for p in PROFILES_DIR.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                profiles.append({
                    "profile_id": data.get("profile_id", p.stem),
                    "name": data.get("name", "Unknown"),
                    "branch": data.get("branch", ""),
                    "year": data.get("year", ""),
                    "skill_level": data.get("skill_level", ""),
                })
            except Exception:
                pass
        return sorted(profiles, key=lambda x: x["name"])

    def delete_profile(self, profile_id: str):
        path = self._path(profile_id)
        if path.exists():
            path.unlink()
            logger.info("Profile deleted: %s", profile_id)
