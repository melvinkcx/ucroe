# UCROE (Use Cached Results On Exception)

UCROE (Use Cached Results On Exception) is a Python decorator that caches a function’s return value and reuses it if the
function raises an exception on subsequent
calls.

Features:

- decorators to cache function return values and return them if subsequent calls raise exception
- multiple built-in cache backends (supports cachetools, Django)
- compatible with [tenacity](https://tenacity.readthedocs.io/en/latest/) retry library
- configurable via decorator parameters, environment variables, and Django settings (if available)

> UCROE doesn't require Django to work properly.

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


@cached_result_on_exception()
def f2(): ...


@cached_result_on_exception(log_exception=True)
def f3(): ...
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

### Django Backend

TODO
