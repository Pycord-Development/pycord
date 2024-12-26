from typing_extensions import TypeAlias, final


@final
class MISSING:
    pass


MissingSentinel: TypeAlias = type[MISSING]

__all__ = ["MISSING", "MissingSentinel"]
