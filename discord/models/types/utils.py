from typing import Literal

from typing_extensions import TypeAlias, final


@final
class MISSING:
    def __bool__(self) -> Literal[False]:
        return False


MissingSentinel: TypeAlias = type[MISSING]

__all__ = ["MISSING", "MissingSentinel"]
