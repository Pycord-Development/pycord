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

from typing import TYPE_CHECKING
from .enums import ApplicationRoleConnectionMetadataType, try_enum
from .utils import MISSING

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.guild import ApplicationRoleConnection as ApplicationRoleConnectionPayload

class ApplicationRoleConnection:
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

    @classmethod
    def from_dict(cls, data: ApplicationRoleConnectionPayload) -> ApplicationRoleConnection:
        return cls(
            type=try_enum(ApplicationRoleConnectionMetadataType, data['type']),
            key=data['key'],
            name=data['name'],
            description=data['description'],
            name_localizations=data.get('name_localizations'),
            description_localizations=data.get('description_localizations'),
        )

    def to_dict(self) -> ApplicationRoleConnectionPayload:
        data = {
            'type': self.type.value,
            'key': self.key,
            'name': self.name,
            'description': self.description,
        }
        if self.name_localizations is not MISSING:
            data['name_localizations'] = self.name_localizations
        if self.description_localizations is not MISSING:
            data['description_localizations'] = self.description_localizations
        return data

