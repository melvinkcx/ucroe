import os

import pytest
from django.core.cache import caches

from ucroe.cache_backend.django import DjangoBackend
from ucroe import CachedResultOnException


@pytest.fixture(autouse=True, scope="session")
def pytest_configure():
    from django.conf import settings

    settings.configure(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            },
            "ucroe": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "KEY_PREFIX": "ucroe_",
            },
            "dummy": {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            },
        }
    )


def test_django_backend_setup_through_django_settings(settings):
    settings.UCROE_BACKEND = "ucroe.cache_backend.django.DjangoBackend"
    settings.UCROE_BACKEND_CONFIG = '{"cache_name": "ucroe"}'

    cached_result_on_exception = CachedResultOnException()

    @cached_result_on_exception
    def f(): ...

    f()

    assert isinstance(cached_result_on_exception.cache, DjangoBackend)
    assert cached_result_on_exception.cache.cache.key_prefix == "ucroe_"


def test_django_backend_setup_through_env_var(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "UCROE_BACKEND": "ucroe.cache_backend.django.DjangoBackend",
            "UCROE_BACKEND_CONFIG": '{"cache_name": "ucroe"}',
        },
    )
    cached_result_on_exception = CachedResultOnException()

    @cached_result_on_exception
    def f(): ...

    f()

    assert isinstance(cached_result_on_exception.cache, DjangoBackend)
    assert cached_result_on_exception.cache.cache.key_prefix == "ucroe_"


def test_config_precedence(settings, mocker):
    """
    django settings should be prioritised over environment variables
    """
    settings.UCROE_BACKEND = "ucroe.cache_backend.django.DjangoBackend"
    settings.UCROE_BACKEND_CONFIG = '{"cache_name": "ucroe"}'

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

    assert isinstance(cached_result_on_exception.cache, DjangoBackend)
    assert cached_result_on_exception.cache.cache.key_prefix == "ucroe_"


def test_django_backend_use_default_cache_when_unspecified(settings):
    settings.UCROE_BACKEND = "ucroe.cache_backend.django.DjangoBackend"
    settings.UCROE_BACKEND_CONFIG = "{}"

    cached_result_on_exception = CachedResultOnException()

    @cached_result_on_exception
    def f(): ...

    f()

    assert isinstance(cached_result_on_exception.cache, DjangoBackend)
    assert cached_result_on_exception.cache.cache.key_prefix == ""


def test_django_backend__get(mocker):
    backend = DjangoBackend(cache_name="dummy")
    spy_django_cache_get = mocker.spy(caches["dummy"], "get")

    backend.get("abc")
    spy_django_cache_get.assert_called_once_with("abc")


def test_django_backend__set(mocker):
    backend = DjangoBackend(cache_name="dummy")
    spy_django_cache_set = mocker.spy(caches["dummy"], "set")

    backend.set("abc", 123)
    spy_django_cache_set.assert_called_once_with("abc", 123)
