from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import fields, is_dataclass, MISSING
from pathlib import Path
from typing import get_origin, get_args, Union
class ConfigSchema(ABC):
    """
    Defines the structure and semantic rules of a configuration.

    Responsibilities:
    - provide default configuration
    - validate merged configuration

    No IO. No state. No secrets.
    """
    config_model: type
    def build(self, raw: dict):
        return self._build_dataclass(self.config_model, raw)

    def _build_dataclass(self, cls, data: dict):
        kwargs = {}
        for field in fields(cls):
            name = field.name
            field_type = field.type
            value = data.get(name)
            if value is None and field.default is MISSING and field.default_factory is MISSING:
                raise ValueError(f"Missing required config field: {name}")
            if is_dataclass(field_type):
                kwargs[name] = self._build_dataclass(field_type, value or {})
            else:
                kwargs[name] = self._coerce(field_type, value)
        return cls(**kwargs)

    def _coerce(self, t, value):
        if value is None:
            return None

        origin = get_origin(t)
        args = get_args(t)

        if origin is list:
            return list(value)

        if origin is Union and type(None) in args:
            non_none= next(a for a in args if a is not type(None))
            return self._coerce(non_none, value)
        if origin is dict:
            return dict(value)

        if t is Path:
            return Path(value)

        return t(value)
