from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Callable, ClassVar, TypeVar, overload

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing_extensions import Self, override

FV = TypeVar("FV", bound="flag_value")
BF = TypeVar("BF", bound="BaseFlags")


class flag_value:
    def __init__(
        self, func: Callable[[Any], int]  # pyright: ignore [reportExplicitAny]
    ):
        self.flag: int = func(None)
        self.__doc__ = func.__doc__

    @overload
    def __get__(self: FV, instance: None, owner: type[BF]) -> FV: ...

    @overload
    def __get__(self, instance: BF, owner: type[BF]) -> bool: ...

    def __get__(
        self, instance: BF | None, owner: type[BF]
    ) -> Any:  # pyright: ignore [reportExplicitAny]
        if instance is None:
            return self
        return instance._has_flag(self.flag)  # pyright: ignore [reportPrivateUsage]

    def __set__(self, instance: BaseFlags, value: bool) -> None:
        instance._set_flag(self.flag, value)  # pyright: ignore [reportPrivateUsage]

    @override
    def __repr__(self):
        return f"<flag_value flag={self.flag!r}>"


class alias_flag_value(flag_value):
    pass


def fill_with_flags(*, inverted: bool = False):
    def decorator(cls: type[BF]):
        cls.VALID_FLAGS = {
            name: value.flag
            for name, value in cls.__dict__.items()
            if isinstance(value, flag_value)
        }

        if inverted:
            max_bits = max(cls.VALID_FLAGS.values()).bit_length()
            cls.DEFAULT_VALUE = -1 + (2**max_bits)
        else:
            cls.DEFAULT_VALUE = 0

        return cls

    return decorator


# n.b. flags must inherit from this and use the decorator above
class BaseFlags:
    VALID_FLAGS: ClassVar[dict[str, int]]
    DEFAULT_VALUE: ClassVar[int]

    value: int

    __slots__: tuple[str] = ("value",)

    def __init__(self, **kwargs: bool):
        self.value = self.DEFAULT_VALUE
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid flag name.")
            setattr(self, key, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # pyright: ignore [reportExplicitAny]
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            # Both JSON and Python accept plain integers as input
            json_schema=core_schema.chain_schema(
                [
                    core_schema.int_schema(),
                    core_schema.no_info_plain_validator_function(cls._from_value),
                ]
            ),
            python_schema=core_schema.union_schema(
                [
                    # Accept existing instances of our class
                    core_schema.is_instance_schema(cls),
                    # Also accept plain integers and convert them
                    core_schema.chain_schema(
                        [
                            core_schema.int_schema(),
                            core_schema.no_info_plain_validator_function(
                                cls._from_value
                            ),
                        ]
                    ),
                ]
            ),
            # Convert to plain int when serializing to JSON
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.value,
                return_schema=core_schema.int_schema(),
                when_used="json",
            ),
        )

    @classmethod
    def _from_value(cls: type[Self], value: int) -> Self:
        self = cls.__new__(cls)
        self.value = value
        return self

    @override
    def __eq__(self, other: Any) -> bool:  # pyright: ignore [reportExplicitAny]
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"'==' not supported between instances of {type(self)} and {type(other)}"
            )
        return isinstance(other, self.__class__) and self.value == other.value

    @override
    def __hash__(self) -> int:
        return hash(self.value)

    @override
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} value={self.value}>"

    def __iter__(self) -> Iterator[tuple[str, bool]]:
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, alias_flag_value):
                continue

            if isinstance(value, flag_value):
                yield name, self._has_flag(value.flag)

    def __and__(self, other: Self | flag_value) -> Self:
        if isinstance(other, self.__class__):
            return self.__class__._from_value(self.value & other.value)
        elif isinstance(other, flag_value):
            return self.__class__._from_value(self.value & other.flag)
        else:
            raise TypeError(
                f"'&' not supported between instances of {type(self)} and {type(other)}"
            )

    def __or__(self, other: Self | flag_value) -> Self:
        if isinstance(other, self.__class__):
            return self.__class__._from_value(self.value | other.value)
        elif isinstance(other, flag_value):
            return self.__class__._from_value(self.value | other.flag)
        else:
            raise TypeError(
                f"'|' not supported between instances of {type(self)} and {type(other)}"
            )

    def __add__(self, other: Self | flag_value) -> Self:
        try:
            return self | other
        except TypeError:
            raise TypeError(
                f"'+' not supported between instances of {type(self)} and {type(other)}"
            )

    def __sub__(self, other: Self | flag_value) -> Self:
        if isinstance(other, self.__class__):
            return self.__class__._from_value(self.value & ~other.value)
        elif isinstance(other, flag_value):
            return self.__class__._from_value(self.value & ~other.flag)
        else:
            raise TypeError(
                f"'-' not supported between instances of {type(self)} and {type(other)}"
            )

    def __invert__(self):
        return self.__class__._from_value(~self.value)

    __rand__: Callable[[Self, Self | flag_value], Self] = __and__
    __ror__: Callable[[Self, Self | flag_value], Self] = __or__
    __radd__: Callable[[Self, Self | flag_value], Self] = __add__
    __rsub__: Callable[[Self, Self | flag_value], Self] = __sub__

    def _has_flag(self, o: int) -> bool:
        return (self.value & o) == o

    def _set_flag(self, o: int, toggle: bool) -> None:
        if toggle:
            self.value |= o
        else:
            self.value &= ~o
