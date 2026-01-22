from __future__ import annotations
from dataclasses import asdict, is_dataclass
import os
import yaml
import argparse
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from platformdirs import user_config_dir
from twitchschedulerpy.modules.core.state_store import StateStore
from twitchschedulerpy.modules.core.secret_store import SecretStore
from twitchschedulerpy.modules.core.config_schema import ConfigSchema


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

    Contract:
    - Provides config/state/secret storage
    - Handles file IO and merging
    - Calls lifecycle hooks in a fixed order


    Subclasses MUST:
    - define default config schema
    - validate semantic correctness

    Subclasses MUST NOT:
    - override load/save logic
    - perform IO in build_default_settings
    """
    version = 3
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
        self.state = StateStore(appname=appname, appauthor=appauthor, version=version)
        self.secrets = SecretStore(
            appname=appname,
        )

        # Runtime containers
        self.raw_settings: dict = {}
        self.config = None

        self.config_path = Path(self.application_directory) / "config.yml"
        self.log_dir = Path(self.application_directory) / "logs"
        self.log_dir.mkdir(exist_ok=True)

        # Lifecycle
        self._init_schema()

    def initialize(self):
        """
        Must be implemented by subclass inheriting from BaseConfigHandler.
        Must call the following, in order:
        
        ```
        self._lifecycle("init:start")
        self.load()
        self._lifecycle("configuration:loaded")
        self.post_init()
        self._lifecycle("post_init")
        ```
        """
        # def initialize(self):
        # Lifecycle
        self._lifecycle("init:start")
        self.load()
        self._lifecycle("configuration:loaded")
        self.post_init()
        self._lifecycle("post_init")

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def _lifecycle(self, step: str) -> None:
        """Internal helper to track lifecycle steps via debug logging."""
        self.logger.debug(f"[lifecycle] {step}")

    # ------------------------------------------------------------------
    # Load / Save configuration
    # ------------------------------------------------------------------
    def load(self) -> None:
        if self.config_path.exists():
            self.load_user_config_and_merge(self.config_path)
        else:
            self.logger.info("No config file found; using defaults")
            self.config = self.schema.build(self.raw_settings)
            self.save()

    def save(self) -> None:
        self.logger.info("Configuration written to file.")
        self.save_to_file(self.config_path)

    # ------------------------------------------------------------------
    # State hooks
    # ------------------------------------------------------------------

    def load_stores(self) -> None:
        self.state.load()

    def save_stores(self) -> None:
        self.state.save()

    # ------------------------------------------------------------------
    # Abstract API – subclasses MUST implement these
    # ------------------------------------------------------------------

    @abstractmethod
    def build_schema(self) -> ConfigSchema:
        """Return the ConfigSchema instance for this application"""
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> None:
        """Validate semantic correctness of applied configuration."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Optional hooks – subclasses MAY override
    # ------------------------------------------------------------------

    def post_init(self) -> None:
        """
        Called after defaults are applied.
        Must be called prior to `load_user_config_and_merge()`.
        """
        pass

    def post_load(self) -> None:
        """Called after config files are loaded/merged."""
        pass

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _init_schema(self) -> None:
        self.schema = self.build_schema()
        if not is_dataclass(self.schema.config_model):
            raise TypeError("config_model must be a dataclass")
        self.raw_settings = asdict(self.schema.config_model())

    # ------------------------------------------------------------------
    # Loading / Saving
    # ------------------------------------------------------------------

    def load_user_config_and_merge(self, path: str | Path) -> None:
        """
        load_user_config_and_merge performs in order:
        - loads the user configuration,
        - merges it into applied settings,
        - calls `self.validate()`; which is abstract and must be implemented
        - calls the `post_load()`-hook

        :param self: Description
        :param path: Path to the configuration file to be loaded by the user
        :type path: str | Path
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            self.raw_settings = self.merge_dicts(self.raw_settings, user_config)
            self.config = self.schema.build(self.raw_settings)
            self.logger.info(f"Loaded config from {path}")
            self._lifecycle(f"user_config:loaded ({path})")

            self.validate()
            self._lifecycle("user_config:validated")

            self.post_load()
            self._lifecycle("post_load")
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {path}")
        except yaml.YAMLError as e:
            self.logger.error(f"YAML error while loading {path}: {e}")

    def save_to_file(self, path: str | Path) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(asdict(self.config), f, allow_unicode=True)
            self.logger.info(f"Config saved to {path}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def export_config(self, path: str | Path) -> None:
        """Export current applied config (explicit API)."""
        self.save_to_file(path)

    # ------------------------------------------------------------------
    # Merging
    # ------------------------------------------------------------------

    def merge_dicts(self, base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key not in base:
                self.logger.warning(f"Ignoring unhandled key '{key}' in user config")
                continue
            if isinstance(base[key], dict) and isinstance(value, dict):
                result[key] = self.merge_dicts(base[key], value)
            else:
                result[key] = value
        return result

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_section(self, name: str):
        return getattr(self.config, name)

    def get_value(self, section: str, key: str, default=None):
        section_obj = getattr(self.config, section)
        return getattr(section_obj, key, default)

    # ------------------------------------------------------------------
    # CLI (optional)
    # ------------------------------------------------------------------

    def load_cli_args(self) -> None:
        """Override if CLI integration is needed."""
        pass
