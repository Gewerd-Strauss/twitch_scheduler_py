from __future__ import annotations
from abc import ABC, abstractmethod


class ConfigSchema(ABC):
    """
    Defines the structure and semantic rules of a configuration.

    Responsibilities:
    - provide default configuration
    - validate merged configuration

    No IO. No state. No secrets.
    """

    @abstractmethod
    def defaults(self) -> dict:
        """Return default configuration structure."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, config: dict) -> None:
        """Validate semantic correctness of the configuration."""
        raise NotImplementedError
