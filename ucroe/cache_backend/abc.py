import abc

from typing import Any

__all__ = ("CacheBackend",)


class CacheBackend(abc.ABC):
    @abc.abstractmethod
    def __init__(self, **kwargs) -> None: ...

    @abc.abstractmethod
    def get(self, key, **kwargs) -> Any: ...

    @abc.abstractmethod
    def set(self, key, value, **kwargs) -> None: ...

    @abc.abstractmethod
    def has(self, key, **kwargs) -> bool: ...
