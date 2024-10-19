import cachetools

from ucroe.cache_backend.abc import CacheBackend


class LRUCacheBackend(CacheBackend):
    def __init__(self, maxsize, **kwargs):
        self.cache = cachetools.LRUCache(maxsize=maxsize, **kwargs)

    def get(self, key, **kwargs):
        return self.cache.get(key, **kwargs)

    def set(self, key, value, **kwargs):
        self.cache[key] = value

    @property
    def current_size(self):
        return self.cache.currsize
