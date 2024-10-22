import cachetools

from ucroe.cache_backend.abc import CacheBackend

__all__ = (
    "FIFOBackend",
    "LFUBackend",
    "LRUBackend",
    "RRBackend",
    "TTLBackend",
    "TLRUBackend",
)


class CachetoolsBackendMixin:
    cache_cls: type[cachetools.Cache]

    def __init__(self, **kwargs):
        if not self.cache_cls:
            raise NotImplementedError(
                f"{self.__class__.__name__}.cache_cls is not defined"
            )

        self.cache = self.cache_cls(**kwargs)

    def get(self, key, **kwargs):
        return self.cache.get(key, **kwargs)

    def set(self, key, value, **kwargs):
        self.cache[key] = value

    def has(self, key, **kwargs) -> bool:
        return key in self.cache

    @property
    def current_size(self):
        return self.cache.currsize


class FIFOBackend(CachetoolsBackendMixin, CacheBackend):
    cache_cls = cachetools.FIFOCache


class LFUBackend(CachetoolsBackendMixin, CacheBackend):
    cache_cls = cachetools.LFUCache


class LRUBackend(CachetoolsBackendMixin, CacheBackend):
    cache_cls = cachetools.LRUCache


class RRBackend(CachetoolsBackendMixin, CacheBackend):
    cache_cls = cachetools.RRCache


class TTLBackend(CachetoolsBackendMixin, CacheBackend):
    cache_cls = cachetools.TTLCache


class TLRUBackend(CachetoolsBackendMixin, CacheBackend):
    cache_cls = cachetools.TLRUCache
