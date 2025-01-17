import os
from unittest.mock import MagicMock

import pytest

from ucroe import CachedResultOnException
from ucroe.cache_backend.abc import CacheBackend
from ucroe.cache_backend.cachetools import TTLBackend


@pytest.fixture
def cached_result_on_exception():
    return CachedResultOnException()


def test_use_cached_value_on_exception(cached_result_on_exception):
    mock_http_call = MagicMock(side_effect=[1, 2, ValueError, 3, 4])

    @cached_result_on_exception
    def f():
        return mock_http_call()

    assert f() == 1
    assert f() == 2
    assert f() == 2  # cached value is returned
    assert f() == 3
    assert f() == 4


def test_raise_when_cached_value_is_absent(cached_result_on_exception):
    gen_fn = MagicMock(side_effect=[ValueError])

    @cached_result_on_exception
    def f():
        return gen_fn()

    with pytest.raises(ValueError):
        f()


@pytest.mark.parametrize("log_exception", [True, False])
def test_option__log_exception(log_exception, caplog, cached_result_on_exception):
    gen_fn = MagicMock(side_effect=[1, ValueError])

    @cached_result_on_exception(log_exception=log_exception)
    def f():
        return gen_fn()

    assert f() == 1  # first call
    assert f() == 1  # second call, it should return the cached value

    if log_exception:
        assert caplog.record_tuples == [
            (
                "ucroe.decorators",
                30,
                "test_option__log_exception -> test_option__log_exception.<locals>.f raised during execution, cached value will be returned",
            )
        ]
    else:
        assert len(caplog.record_tuples) == 0


def test_decorator_with_custom_cache_backend(cached_result_on_exception):
    class CustomCacheBackend(CacheBackend):
        def __init__(self):
            self._cache = {}

        def get(self, key, **kwargs):
            return self._cache.get(key)

        def set(self, key, value, **kwargs):
            self._cache[key] = value

        def has(self, key, **kwargs):
            return key in self._cache

    custom_cache_backend = CustomCacheBackend()

    @cached_result_on_exception(cache=custom_cache_backend)
    def f1():
        return True

    @cached_result_on_exception()
    def f2():
        return False

    assert f1()
    assert f1()
    assert f1()
    assert not f2()
    assert not f2()

    assert len(custom_cache_backend._cache) == 1


def test_on_exception_callback(cached_result_on_exception):
    mock_cb = MagicMock()

    gen_fn = MagicMock(side_effect=[1, ValueError, ValueError, ValueError, 2])

    @cached_result_on_exception(on_exception=mock_cb)
    def f():
        return gen_fn()

    assert f() == 1
    mock_cb.assert_not_called()

    assert f() == 1
    assert mock_cb.call_count == 1
    assert f() == 1
    assert mock_cb.call_count == 2
    assert f() == 1
    assert mock_cb.call_count == 3

    assert f() == 2
    assert mock_cb.call_count == 3


def test_set_backend_through_env_var(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "UCROE_BACKEND": "ucroe.cache_backend.cachetools.TTLBackend",
            "UCROE_BACKEND_CONFIG": '{"ttl": 5, "maxsize": 100}',
        },
    )
    cached_result_on_exception = CachedResultOnException()

    @cached_result_on_exception
    def f(): ...

    f()

    assert isinstance(cached_result_on_exception.cache, TTLBackend)


def test_decorated_func_properly_wrapped(cached_result_on_exception):
    @cached_result_on_exception
    def f(): ...

    assert f.__qualname__ == "test_decorated_func_properly_wrapped.<locals>.f"


def test_decorating_without_options_1(cached_result_on_exception):
    mocked_value = MagicMock()

    @cached_result_on_exception
    def f():
        return mocked_value

    assert f() == mocked_value


def test_decorating_without_options_2(cached_result_on_exception):
    mocked_value = MagicMock()

    @cached_result_on_exception()
    def f():
        return mocked_value

    assert f() == mocked_value


def test_decorating_with_options_1(cached_result_on_exception):
    mocked_value = MagicMock()

    @cached_result_on_exception(log_exception=True)
    def f():
        return mocked_value

    assert f() == mocked_value


def test_decorating_func_that_returns_none(cached_result_on_exception):
    gen_fn = MagicMock(side_effect=[None, ValueError])

    @cached_result_on_exception
    def f():
        return gen_fn()

    assert f() is None
    assert f() is None
