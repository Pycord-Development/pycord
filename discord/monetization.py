"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
)

from .enums import SKUType, EntitlementType, try_enum
from .flags import SKUFlags
from .utils import _get_as_snowflake, parse_time, MISSING
from .mixins import Hashable

if TYPE_CHECKING:
    from datetime import datetime

    from .types.monetization import (
        SKU as SKUPayload,
        Entitlement as EntitlementPayload,
    )
    from .state import ConnectionState


__all__ = (
    "SKU",
    "Entitlement",
)


class SKU(Hashable):
    __slots__ = (
        "id",
        "type",
        "application_id",
        "name",
        "slug",
        "flags",
    )
    def __init__(self, *, data: SKUPayload, state: ConnectionState) -> None:
        self._state = state
        self.id: int = int(data["id"])
        self.type: SKUType = try_enum(SKUType, data["type"])
        self.application_id: int = int(data["application_id"])
        self.name: str = data["name"]
        self.slug: str = data["slug"]
        self.flags: SKUFlags = SKUFlags(data["flags"])

    def __repr__(self) -> str:
        return (
            f"<SKU id={self.id} name={self.name!r} application_id={self.application_id} "
            f"slug={self.slug!r} flags={self.flags!r}>"
        )

    def __str__(self) -> str:
        return self.name


class Entitlement(Hashable):
    __slots__ = (
        "_state",
        "id",
        "sku_id",
        "application_id",
        "user_id",
        "type",
        "deleted",
        "starts_at",
        "ends_at",
    )
    def __init__(self, *, data: EntitlementPayload, state: ConnectionState) -> None:
        self._state = state
        self.id: int = int(data["id"])
        self.sku_id: int = int(data["sku_id"])
        self.application_id: int = int(data["application_id"])
        self.user_id: int | MISSING = _get_as_snowflake(data, "user_id") or MISSING
        self.type: EntitlementType = try_enum(EntitlementType, data["type"])
        self.deleted: bool = data["deleted"]
        self.starts_at: datetime | MISSING = parse_time(data.get("starts_at")) or MISSING
        self.ends_at: datetime | MISSING = parse_time(data.get("ends_at")) or MISSING

    def __repr__(self) -> str:
        return (
            f"<Entitlement id={self.id} sku_id={self.sku_id} application_id={self.application_id} "
            f"user_id={self.user_id} type={self.type} deleted={self.deleted} "
            f"starts_at={self.starts_at} ends_at={self.ends_at}>"
        )
    
    async def delete(self) -> None:
        """|coro|

        Deletes a test entitlement.

        Raises
        ------
        HTTPException
            Deleting the entitlement failed.
        """
        await self._state.http.delete_test_entitlement(self.id)
