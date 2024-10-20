__all__ = (
    "BaseUCROEException",
    "DjangoSettingNotFound",
)


class BaseUCROEException(Exception): ...


class DjangoSettingNotFound(BaseUCROEException): ...
