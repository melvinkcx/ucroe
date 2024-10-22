from typing import Any

from django.core.cache import caches

from ucroe.cache_backend.abc import CacheBackend
from ucroe.config import HAS_DJANGO
from ucroe.exceptions import DjangoSettingNotFound

__all__ = ("DjangoBackend",)


class DjangoBackend(CacheBackend):
    def __init__(self, cache_name: str | None = None, **kwargs):
        if not HAS_DJANGO:
            raise DjangoSettingNotFound

        self.cache = caches[cache_name or "default"]

    def get(self, key, **kwargs) -> Any:
        return self.cache.get(key, **kwargs)

    def set(self, key, value, **kwargs) -> None:
        return self.cache.set(key, value, **kwargs)

    def has(self, key, **kwargs) -> bool:
        return self.cache.has_key(key, **kwargs)
