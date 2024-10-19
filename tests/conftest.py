import pytest


@pytest.fixture(scope="function", autouse=True)
def _dj_autoclear_mailbox() -> None:
    # See: https://github.com/pytest-dev/pytest-django/issues/993
    # Override the `_dj_autoclear_mailbox` test fixture in `pytest_django`.
    pass
