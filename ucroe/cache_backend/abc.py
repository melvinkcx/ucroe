import abc

__all__ = ("CacheBackend",)


class CacheBackend(abc.ABC):
    @abc.abstractmethod
    def __init__(self, **kwargs): ...

    @abc.abstractmethod
    def get(self, key, **kwargs): ...

    @abc.abstractmethod
    def set(self, key, value, **kwargs): ...
