import functools
import json
import os
from contextlib import suppress
from functools import cached_property
from typing import TypedDict, Mapping

try:
    from django.conf import settings

    HAS_DJANGO = True
except ImportError:
    HAS_DJANGO = False


class ConfigDict(TypedDict, total=False):
    LOG_EXCEPTION_BY_DEFAULT: bool
    HAS_DJANGO: bool
    BACKEND: str
    BACKEND_CONFIG: dict


class _Exception(Exception): ...


class DjangoNotAvailable(_Exception): ...


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
        "HAS_DJANGO": False,
        "BACKEND": "ucroe.cache_backend.cachetools.LRUCacheBackend",
        "BACKEND_CONFIG": {"maxsize": 100},
    }

    def __getattr__(self, name: str):
        if (u_name := name.upper()) in self.DEFAULTS:
            return self.get_config(u_name)

    @cached_property
    def backend_config(self):
        value = self.get_config("BACKEND_CONFIG")

        if isinstance(value, str):
            with suppress(ValueError):
                value = json.loads(value)

        if isinstance(value, Mapping):
            return value

        return {}

    @functools.cache
    def get_config(self, name: str):
        # 1. try getting it from django settings
        try:
            return self.get_from_django_settings(name)
        except DjangoNotAvailable:
            ...

        # 2. get it from env var
        if value := os.getenv(name):
            return value

        # 3. use the default value
        return self.DEFAULTS.get(name)

    @staticmethod
    def get_from_django_settings(name: str):
        if not HAS_DJANGO:
            raise DjangoNotAvailable

        from django.core.exceptions import ImproperlyConfigured

        try:
            return getattr(settings, name)
        except ImproperlyConfigured:
            raise DjangoNotAvailable
