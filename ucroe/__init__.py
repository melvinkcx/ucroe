from importlib import metadata
from importlib.metadata import PackageNotFoundError

try:
    # see: https://github.com/python-poetry/poetry/issues/144#issuecomment-1488038660
    __version__ = metadata.version("ucroe")
except PackageNotFoundError:
    # this will only occur during development
    __version__ = "unknown"
