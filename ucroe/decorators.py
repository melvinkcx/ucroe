import functools
import importlib
import inspect
import logging
import sys
from typing import Any, Callable, ParamSpec, TypedDict, TypeVar

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

from ucroe.cache_backend.abc import CacheBackend
from ucroe.config import GlobalConfig

logger = logging.getLogger(__name__)

__all__ = (
    "cached_result_on_exception",
    "CachedResultOnException",
    "DecoratorOptionDict",
)

P = ParamSpec("P")
R = TypeVar("R")


def get_backend(backend: str) -> type[CacheBackend]:
    path, backend_cls = backend.rsplit(".", 1)
    module = importlib.import_module(path)

    return getattr(module, backend_cls)


class DecoratorOptionDict(TypedDict, total=False):
    cache: CacheBackend
    log_exception: bool
    on_exception: Callable


class CachedResultOnException:
    def __init__(self) -> None:
        self._config = GlobalConfig()
        self._cache = None

    @property
    def cache(self):
        if not self._cache:
            backend_cls = get_backend(self._config.backend)
            backend_conf = self._config.backend_config
            self._cache = backend_cls(**backend_conf)

        return self._cache

    def __call__(
        self,
        func_: Callable[P, R] | None = None,
        **options: Unpack[DecoratorOptionDict],
    ):
        if func_ is None:
            return self._gen_wrapper_with_options(**options)
        else:
            return self._gen_wrapper_with_options(**options)(func=func_)

    @staticmethod
    def key_formatter(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Any:
        # cache key: the positional and keyword arguments to the function must be hashable
        return (
            id(func),
            func.__module__,
            func.__qualname__,
            args,
            tuple(sorted(kwargs.items())),
        )

    def run(
        self,
        options: DecoratorOptionDict,
        func: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        c_key = self.key_formatter(func, *args, **kwargs)
        cache = options.get("cache") or self.cache

        try:
            ret_val = func(*args, **kwargs)
            cache.set(c_key, ret_val)
        except Exception as exc:
            ret_val = self._get_or_raise(cache, c_key)
            self._handle_log_exception_option(func=func, options=options, exc_info=exc)
            self._handle_on_exception_hook(func=func, options=options, exc_info=exc)

        return ret_val

    @staticmethod
    def _get_or_raise(cache, key):
        cached_value = cache.get(key)
        if cached_value is None and not cache.has(key):
            raise

        return cached_value

    def _handle_log_exception_option(
        self, func: Callable[P, R], options: DecoratorOptionDict, exc_info: Exception
    ):
        if options.get("log_exception", self._config.LOG_EXCEPTION_BY_DEFAULT):
            caller_frame = inspect.getouterframes(inspect.currentframe())
            caller_fn: str = caller_frame[3].function
            logger.warning(
                f"{caller_fn} -> {func.__qualname__} raised during execution, cached value will be returned",
                exc_info=exc_info,
            )

    def _handle_on_exception_hook(
        self, func: Callable[P, R], options: DecoratorOptionDict, exc_info: Exception
    ):
        if (on_exception_fn := options.get("on_exception")) and callable(
            on_exception_fn
        ):
            try:
                on_exception_fn(exc_info)
            except Exception as exc_:
                logger.warning(
                    f"on_exception hook of {func.__qualname__} raised during execution",
                    exc_info=exc_,
                )

    def _gen_wrapper_with_options(self, **options: Unpack[DecoratorOptionDict]):
        def gen_wrapper(func: Callable[P, R]) -> Callable[P, R]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return self.run(options, func, *args, **kwargs)

            return wrapper

        return gen_wrapper


cached_result_on_exception = CachedResultOnException()
