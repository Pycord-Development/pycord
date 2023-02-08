"""
The MIT License (MIT)

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

from typing import TYPE_CHECKING

from .enums import ApplicationRoleConnectionMetadataType, try_enum
from .utils import MISSING

if TYPE_CHECKING:
    from .types.application_role_connection import (
        ApplicationRoleConnectionMetadata as ApplicationRoleConnectionMetadataPayload,
    )

__all__ = ("ApplicationRoleConnectionMetadata",)


class ApplicationRoleConnectionMetadata:
    r"""Represents role connection metadata for a Discord application.

    .. versionadded:: 2.4

    Parameters
    ----------
    type: :class:`ApplicationRoleConnectionMetadataType`
        The type of metadata value.
    key: :class:`str`
        The key for this metadata field.
        May only be the ``a-z``, ``0-9``, or ``_`` characters, with a maximum of 50 characters.
    name: :class:`str`
        The name for this metadata field. Maximum 100 characters.
    description: :class:`str`
        The description for this metadata field. Maximum 200 characters.
    name_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        The name localizations for this metadata field. The values of this should be ``"locale": "name"``.
        See `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
    description_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        The description localizations for this metadata field. The values of this should be ``"locale": "name"``.
        See `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
    """

    __slots__ = (
        "type",
        "key",
        "name",
        "description",
        "name_localizations",
        "description_localizations",
    )

    def __init__(
        self,
        *,
        type: ApplicationRoleConnectionMetadataType,
        key: str,
        name: str,
        description: str,
        name_localizations: dict[str, str] = MISSING,
        description_localizations: dict[str, str] = MISSING,
    ):
        self.type: ApplicationRoleConnectionMetadataType = type
        self.key: str = key
        self.name: str = name
        self.name_localizations: dict[str, str] = name_localizations
        self.description: str = description
        self.description_localizations: dict[str, str] = description_localizations

    def __repr__(self):
        return (
            "<ApplicationRoleConnectionMetadata "
            f"type={self.type!r} "
            f"key={self.key!r} "
            f"name={self.name!r} "
            f"description={self.description!r} "
            f"name_localizations={self.name_localizations!r} "
            f"description_localizations={self.description_localizations!r}>"
        )

    def __str__(self):
        return self.name

    @classmethod
    def from_dict(
        cls, data: ApplicationRoleConnectionMetadataPayload
    ) -> ApplicationRoleConnectionMetadata:
        return cls(
            type=try_enum(ApplicationRoleConnectionMetadataType, data["type"]),
            key=data["key"],
            name=data["name"],
            description=data["description"],
            name_localizations=data.get("name_localizations"),
            description_localizations=data.get("description_localizations"),
        )

    def to_dict(self) -> ApplicationRoleConnectionMetadataPayload:
        data = {
            "type": self.type.value,
            "key": self.key,
            "name": self.name,
            "description": self.description,
        }
        if self.name_localizations is not MISSING:
            data["name_localizations"] = self.name_localizations
        if self.description_localizations is not MISSING:
            data["description_localizations"] = self.description_localizations
        return data
