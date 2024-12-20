from typing_extensions import TypeAlias, final, override


@final
class MISSING:
    pass


MissingSentinel: TypeAlias = type[MISSING]

__all__ = ["MISSING", "MissingSentinel"]
