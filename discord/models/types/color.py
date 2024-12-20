from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing_extensions import Self, final, override


@final
class Color(int):
    """Represents a color."""

    def __new__(cls, value: int) -> Self:
        # allow for hex str #......
        if isinstance(value, str) and value.startswith("#") and len(value) == 7:
            value = int(value[1:], 16)
        return super().__new__(cls, value)

    def _get_byte(self, byte: int) -> int:
        return (self >> (8 * byte)) & 0xFF

    @override
    def __repr__(self) -> str:
        return f"<Colour value={self}>"

    @override
    def __str__(self) -> str:
        return f"#{self:0>6x}"

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # pyright: ignore [reportExplicitAny]
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Define how Pydantic should handle validation and serialization of Snowflakes"""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.int_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    core_schema.int_schema(),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                int, return_schema=core_schema.int_schema(), when_used="json"
            ),
        )


Colour = Color
__all__ = ["Color", "Colour"]
