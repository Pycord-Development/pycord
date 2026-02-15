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

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import ConnectionState

from .asset import Asset
from .types.collectibles import Collectibles as CollectiblesPayload
from .types.collectibles import Nameplate as NameplatePayload


class Collectibles:
    """
    Represents all the User's equipped collectibles.

    .. versionadded:: 2.8

    Attributes
    ----------
    nameplate: :class:`Nameplate`
        The user's nameplate.
    """

    def __init__(self, data: CollectiblesPayload, state: "ConnectionState") -> None:
        if data and data.get("nameplate"):
            self.nameplate = Nameplate(data=data["nameplate"], state=state)
        else:
            self.nameplate = None
        self._state = state

    def __repr__(self) -> str:
        return f"<Collectibles nameplate={self.nameplate}>"


class Nameplate:
    """
    Represents a Discord Nameplate.

    .. versionadded:: 2.7

    Attributes
    ----------
    sku_id: :class:`int`
        The SKU ID of the nameplate.
    palette: :class:`str`
        The color palette of the nameplate.
    """

    def __init__(self, data: NameplatePayload, state: "ConnectionState") -> None:
        self.sku_id: int = data["sku_id"]
        self.palette: str = data["palette"]
        self._label: str = data["label"]
        self._asset: str = data["asset"]
        self._state: "ConnectionState" = state

    def __repr__(self) -> str:
        return f"<Nameplate sku_id={self.sku_id} palette={self.palette}>"

    @cached_property
    def static_asset(self) -> Asset:
        """
        The static :class:`Asset` of this nameplate.

        .. versionadded:: 2.7
        """
        return Asset._from_collectible(self._state, self._asset)

    @cached_property
    def animated_asset(self) -> Asset:
        """
        The animated :class:`Asset` of this nameplate.

        .. versionadded:: 2.7
        """
        return Asset._from_collectible(self._state, self._asset, animated=True)


__all__ = (
    "Collectibles",
    "Nameplate",
)
