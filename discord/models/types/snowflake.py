from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing_extensions import override

DISCORD_EPOCH = 1420070400000  # First second of 2015


class Snowflake(int):
    """Represents a Discord snowflake ID."""

    @classmethod
    def from_datetime(cls, dt: datetime) -> Snowflake:
        """Creates a Snowflake from a datetime object."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        unix_ms = int(dt.timestamp() * 1000)
        discord_ms = unix_ms - DISCORD_EPOCH
        return cls(discord_ms << 22)

    @property
    def timestamp(self) -> datetime:
        """Returns the creation time of this snowflake."""
        ms = (self >> 22) + DISCORD_EPOCH
        return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)

    @property
    def worker_id(self) -> int:
        """Returns the internal worker ID."""
        return (self & 0x3E0000) >> 17

    @property
    def process_id(self) -> int:
        """Returns the internal process ID."""
        return (self & 0x1F000) >> 12

    @property
    def increment(self) -> int:
        """Returns the increment count."""
        return self & 0xFFF

    @property
    def id(self) -> int:
        return int(self)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # pyright: ignore [reportExplicitAny]
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Define how Pydantic should handle validation and serialization of Snowflakes"""

        def validate_from_int(value: int) -> Snowflake:
            if value < 0:
                raise ValueError("Snowflake cannot be negative")
            return cls(value)

        from_int_schema = core_schema.chain_schema(
            [
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(validate_from_int),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_int_schema,
            python_schema=core_schema.union_schema(
                [
                    # Check if it's already a Snowflake instance
                    core_schema.is_instance_schema(cls),
                    from_int_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                str, return_schema=core_schema.str_schema(), when_used="json"
            ),
        )

    @override
    def __repr__(self) -> str:
        return f"<Snowflake {int(self)}>"

    @override
    def __str__(self) -> str:
        return str(int(self))


__all__ = ["Snowflake"]
