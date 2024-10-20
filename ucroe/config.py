import json
import os
from contextlib import suppress
from typing import Mapping, TypedDict

from ucroe.exceptions import DjangoSettingNotFound

try:
    from django.conf import settings

    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False

__all__ = (
    "HAS_DJANGO",
    "ConfigDict",
    "GlobalConfig",
)


class ConfigDict(TypedDict, total=False):
    LOG_EXCEPTION_BY_DEFAULT: bool
    BACKEND: str
    BACKEND_CONFIG: dict


class GlobalConfig:
    """
    1. get config from django settings
    2. get from environment variables
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    DEFAULTS: ConfigDict = {
        "LOG_EXCEPTION_BY_DEFAULT": False,
        "BACKEND": "ucroe.cache_backend.cachetools.LRUBackend",
        "BACKEND_CONFIG": {"maxsize": 100},
    }

    def __getattr__(self, name: str):
        if (u_name := name.upper()) in self.DEFAULTS:
            return self.get_config(u_name)

    @property
    def backend_config(self):
        value = self.get_config("BACKEND_CONFIG")

        if isinstance(value, str):
            with suppress(ValueError):
                value = json.loads(value)

        if isinstance(value, Mapping):
            return value

        return {}

    def get_config(self, name: str):
        prefixed_name = f"UCROE_{name}"

        # 1. try getting it from django settings
        try:
            return self.get_from_django_settings(prefixed_name)
        except DjangoSettingNotFound:
            ...

        # 2. get it from env var
        if value := os.environ.get(prefixed_name):
            return value

        # 3. use the default value
        return self.DEFAULTS.get(name)

    @staticmethod
    def get_from_django_settings(name: str):
        if not HAS_DJANGO:
            raise DjangoSettingNotFound

        from django.core.exceptions import ImproperlyConfigured

        try:
            if hasattr(settings, name):
                return getattr(settings, name)
        except ImproperlyConfigured:
            raise DjangoSettingNotFound

        raise DjangoSettingNotFound
