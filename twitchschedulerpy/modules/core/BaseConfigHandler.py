from __future__ import annotations

import os
import yaml
import argparse
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from platformdirs import user_config_dir
from modules.core.state_store import StateStore
from modules.core.secret_store import SecretStore

class BaseConfigHandler(ABC):
    """
    Generic configuration infrastructure.

    Responsibilities:
    - config directory resolution
    - YAML load/save
    - merging defaults with user config
    - validation hooks
    - lifecycle hooks

    No domain logic allowed.
    """

    def __init__(
        self,
        *,
        appname: str,
        appauthor: str,
        version: str,
        loglevel: int | None = None,
        is_gui: bool | None = None,
    ):
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        )
        if loglevel is not None:
            self.logger.setLevel(loglevel)

        self.appname = appname
        self.appauthor = appauthor
        self.version = version
        self.is_gui = is_gui

        # Base application config directory
        self.application_directory = os.path.normpath(
            user_config_dir(
                appname=self.appname,
                appauthor=self.appauthor,
                version=self.version,
            )
        )
        os.makedirs(self.application_directory, exist_ok=True)

        # Core stores
        self.state = StateStore(
            appname=appname,
            appauthor=appauthor,
            version=version
        )
        self.secrets = SecretStore(
            appname=appname,
        )


        # Runtime containers
        self.default_settings: dict = {}
        self.applied_settings: dict = {}

        # Lifecycle
        self._init_defaults()
        self.apply_defaults()
        self.post_init()

    # ------------------------------------------------------------------
    # Abstract API – subclasses MUST implement these
    # ------------------------------------------------------------------

    @abstractmethod
    def build_default_settings(self) -> dict:
        """Return default configuration dict."""
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> None:
        """Validate semantic correctness of applied configuration."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Optional hooks – subclasses MAY override
    # ------------------------------------------------------------------

    def post_init(self) -> None:
        """Called after defaults are applied."""
        pass

    def post_load(self) -> None:
        """Called after config files are loaded/merged."""
        pass

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _init_defaults(self) -> None:
        self.default_settings = self.build_default_settings()

    def apply_defaults(self) -> None:
        self.applied_settings = self.default_settings.copy()

    # ------------------------------------------------------------------
    # Loading / Saving
    # ------------------------------------------------------------------

    def load_from_file(self, path: str | Path) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            self.applied_settings = self.merge_dicts(self.applied_settings, user_config)
            self.logger.info(f"Loaded config from {path}")
            self.validate()
            self.post_load()
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {path}")
        except yaml.YAMLError as e:
            self.logger.error(f"YAML error while loading {path}: {e}")

    def save_to_file(self, path: str | Path) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(self.applied_settings, f, allow_unicode=True)
            self.logger.info(f"Config saved to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def export_config(self, path: str | Path) -> None:
        """Export current applied config (explicit API)."""
        self.save_to_file(path)

    # ------------------------------------------------------------------
    # Merging
    # ------------------------------------------------------------------

    def merge_dicts(
        self,
        dict_default: dict,
        dict_user: dict,
        allowed_missing_keys: list[str] | None = None,
    ) -> dict:
        if allowed_missing_keys is None:
            allowed_missing_keys = []

        merged = dict_default.copy()

        for key, value in dict_user.items():
            if key not in dict_default:
                if key in allowed_missing_keys:
                    self.logger.warning(
                        f"Allowed extra key '{key}' found in user config."
                    )
                    merged[key] = value
                else:
                    self.logger.error(f"Unhandled key '{key}' found in user config.")
                continue

            if isinstance(dict_default[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_dicts(
                    dict_default[key], value, allowed_missing_keys
                )
            else:
                merged[key] = value

        for key in dict_default:
            if key not in dict_user:
                self.logger.debug(f"Using default value for missing key '{key}'.")

        return merged

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_section(self, name: str):
        return self.applied_settings.get(name)

    def get_value(self, section: str, key: str, default=None):
        return self.applied_settings.get(section, {}).get(key, default)

    # ------------------------------------------------------------------
    # CLI (optional)
    # ------------------------------------------------------------------

    def load_cli_args(self) -> None:
        """Override if CLI integration is needed."""
        pass
