from __future__ import annotations

import os
import yaml
import logging
from pathlib import Path
from platformdirs import user_state_dir


class StateStore:
    """
    Persistent runtime state.
    Safe to delete at any time.
    """

    def __init__(self, *, appname: str, appauthor: str, version: str):
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        )

        self.base_dir = Path(
            user_state_dir(
                appname=appname,
                appauthor=appauthor,
                version=version,
            )
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.base_dir / f"{name}.yml"

    def load(self, name: str) -> dict:
        path = self._path(name)
        if not path.exists():
            return {}

        try:
            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self.logger.error(f"Failed to load state '{name}': {e}")
            return {}

    def save(self, name: str, data: dict) -> None:
        path = self._path(name)
        try:
            with path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            self.logger.error(f"Failed to save state '{name}': {e}")

    def delete(self, name: str) -> None:
        path = self._path(name)
        if path.exists():
            path.unlink()
