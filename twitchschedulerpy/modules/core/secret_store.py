from __future__ import annotations

import logging
import keyring
from keyring.backend import KeyringBackend


class SecretStore:
    """
    Secure credential storage using OS keyring.
    """

    def __init__(self, *, appname: str):
        self.appname = appname
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__qualname__}"
        )

        self._keyring = keyring.get_keyring()

        if not isinstance(self._keyring, KeyringBackend) or self._keyring.priority < 1:
            self.logger.warning(
                "No secure keyring backend detected. Secrets may not be stored securely."
            )

    def get(self, key: str) -> str | None:
        return keyring.get_password(self.appname, key)

    def set(self, key: str, value: str) -> None:
        keyring.set_password(self.appname, key, value)

    def delete(self, key: str) -> None:
        try:
            keyring.delete_password(self.appname, key)
        except keyring.errors.PasswordDeleteError:
            pass
