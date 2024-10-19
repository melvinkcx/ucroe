from django.core.cache import caches

from ucroe.cache_backend.abc import CacheBackend
from ucroe.config import HAS_DJANGO
from ucroe.exceptions import DjangoSettingNotFound


class DjangoBackend(CacheBackend):
    def __init__(self, cache_name: str | None = None, **kwargs):
        if not HAS_DJANGO:
            raise DjangoSettingNotFound

        self.cache = caches[cache_name or "default"]

    def get(self, key, **kwargs):
        return self.cache.get(key, **kwargs)

    def set(self, key, value, **kwargs):
        return self.cache.set(key, value, **kwargs)
