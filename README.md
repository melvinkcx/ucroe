# UCROE (Use Cached Results On Exception)

UCROE (Use Cached Results On Exception) provides Python decorators that cache a function’s return value and reuse it if
the
function raises an exception on subsequent calls.

Features:

- decorators to cache function return values and return them if subsequent calls raise an exception
- multiple built-in cache backends (supports cachetools, Django)
- compatible with [tenacity](https://tenacity.readthedocs.io/en/latest/), a retry library
- configurable via decorator parameters, environment variables, and Django settings (if available)

> UCROE is a standalone library. It doesn't require Django but works well with it.

To be implemented:

- support async functions
- support methods

---

# Getting Started

## Installation

```shell
pip install ucroe
```

## Basic Usage

```python
from ucroe import cached_result_on_exception


@cached_result_on_exception
def f1(): ...
```

### Expected Behaviour When Cached Value Is Present

```python
from ucroe import cached_result_on_exception
from unittest.mock import MagicMock

mock_http_call = MagicMock(side_effect=[1, 2, ValueError, 3, 4])


@cached_result_on_exception
def f():
    return mock_http_call()


assert f() == 1
assert f() == 2
assert f() == 2  # cached value is returned
assert f() == 3
assert f() == 4
```

### Expected Behaviour When There Is No Cached Value

```python
from unittest.mock import MagicMock

from ucroe import cached_result_on_exception

gen_fn = MagicMock(side_effect=[ValueError])  # raises during the 1st invocation


@cached_result_on_exception
def f():
    return gen_fn()


f()  # raises ValueError
```

## Supported Configuration

UCROE supports the following configs, they can be configured as environment variables or Django settings, if available.
In case of conflict, Django settings will take precedence.

- `UCROE_LOG_EXCEPTION_BY_DEFAULT`: (default: `False`) when set, exception raised within the wrapped function will be
  logged with log level `warning`.
- `UCROE_BACKEND`: (default: `ucroe.cache_backend.cachetools.LRUBackend`) the cache backend to use
- `UCROE_BACKEND_CONFIG`: (default: `'{"maxsize": 100}'`) JSON serialized string that will be used to instantiate the
  cache backend

## Configuring Cache Backend

By default, `@cached_result_on_exception` uses `ucroe.cache_backend.cachetools.LRUBackend`, which itself is a wrapper
of [`cachetools.LRUCache`](https://cachetools.readthedocs.io/en/latest/#cachetools.LRUCache).

UCROE comes with a set of built-in backends:

- `ucroe.cache_backend.cachetools.FIFOBackend`
- `ucroe.cache_backend.cachetools.LFUBackend`
- `ucroe.cache_backend.cachetools.LRUBackend`
- `ucroe.cache_backend.cachetools.RRBackend`
- `ucroe.cache_backend.cachetools.TTLBackend`
- `ucroe.cache_backend.cachetools.TLRUBackend`
- `ucroe.cache_backend.django.DjangoBackend`

Each cachetools backend is merely a wrapper to the corresponding cache provided by cachetools.

### Using Django Backend

This library can be configured to use Django cache framework.
To do so, simple specify `ucroe.cache_backend.django.DjangoBackend` as the cache backend. Eg:

```python
# in your Django settings 
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "ucroe": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "KEY_PREFIX": "ucroe_",
    },
}

# Add the following settings:
UCROE_BACKEND = "ucroe.cache_backend.django.DjangoBackend"
# Optionally, you can also specify the Django cache to use.
# When unspecified, the `default` cache will be used
UCROE_BACKEND_CONFIG = {"cache_name": "ucroe"}
```

In other parts of your code, simple import and decorate your functions with `@cached_results_on_exception`:

```python
from ucroe import cached_result_on_exception


@cached_result_on_exception
def my_func(*args):
    ...
```

## Using the decorators

It can be used with or without parenthesis

```python
from ucroe import cached_result_on_exception


@cached_result_on_exception
def f1(): ...


@cached_result_on_exception()
def f2(): ...
```

It also accepts the following parameters:

- `log_exception: bool`: when set to `True`, a warning log will emit when the wrapped function raises an exception
  ```python
  from ucroe import cached_result_on_exception
  
  @cached_result_on_exception(log_exception=True)
  def f1(): ...
  ```
- `on_exception: Callable[[Exception], None]`: a hook that will be called when the wrapped function raises
  ```python
  import logging
  from ucroe import cached_result_on_exception
  
  logger = logging.getLogger(__name__)
  
  
  def on_exception(exc):
      logger.error("BOOM!", exc_info=exc)
  
  
  @cached_result_on_exception(on_exception=on_exception)
  def f1(): ...
  
  
  f1()  # If f1() raises, a log with message `error: BOOM!` and the stack trace will be emitted.
  ```
