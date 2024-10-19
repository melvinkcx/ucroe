from unittest.mock import MagicMock

import pytest

from ucroe.cache_backend.abc import CacheBackend
from ucroe.decorators import cached_result_on_exception


def test_use_cached_value_on_exception():
    mock_http_call = MagicMock(side_effect=[1, 2, ValueError, 3, 4])

    @cached_result_on_exception
    def f():
        return mock_http_call()

    assert f() == 1
    assert f() == 2
    assert f() == 2  # cached value is returned
    assert f() == 3
    assert f() == 4


def test_raise_when_cached_value_is_absent():
    gen_fn = MagicMock(side_effect=[ValueError])

    @cached_result_on_exception
    def f():
        return gen_fn()

    with pytest.raises(ValueError):
        f()


@pytest.mark.parametrize("log_exception", [True, False])
def test_option__log_exception(log_exception, caplog):
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


def test_decorator_with_custom_cache_backend():
    class CustomCacheBackend(CacheBackend):
        def __init__(self):
            self._cache = {}

        def get(self, key, **kwargs):
            return self._cache.get(key)

        def set(self, key, value, **kwargs):
            self._cache[key] = value

    custom_cache_backend = CustomCacheBackend()

    @cached_result_on_exception(cache=custom_cache_backend)
    def f():
        return True

    assert f()
    assert f()
    assert f()

    assert len(custom_cache_backend._cache) == 1


def test_on_exception_callback():
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


def test_decorated_func_properly_wrapped():
    @cached_result_on_exception
    def f(): ...

    assert f.__qualname__ == "test_decorated_func_properly_wrapped.<locals>.f"


def test_decorating_without_options_1():
    mocked_value = MagicMock()

    @cached_result_on_exception
    def f():
        return mocked_value

    assert f() == mocked_value


def test_decorating_without_options_2():
    mocked_value = MagicMock()

    @cached_result_on_exception()
    def f():
        return mocked_value

    assert f() == mocked_value


def test_decorating_with_options_1():
    mocked_value = MagicMock()

    @cached_result_on_exception(log_exception=True)
    def f():
        return mocked_value

    assert f() == mocked_value
