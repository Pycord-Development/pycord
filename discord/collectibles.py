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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import ConnectionState

from .asset import Asset
from .enums import NameplatePalette
from .types.collectibles import Nameplate as NameplatePayload


class Nameplate:
    """
    Represents a Discord Nameplate.

    .. versionadded:: 2.7

    Attributes
    ----------
        sku_id: int
            The SKU ID of the nameplate.
        palette: NameplatePalette
            The color palette of the nameplate.
    """

    def __init__(self, data: NameplatePayload, state: "ConnectionState") -> None:
        self.sku_id: int = data["sku_id"]
        self.palette: NameplatePalette = data["palette"]
        self._label: str = data["label"]
        self._asset: str = data["asset"]
        self._state: "ConnectionState" = state

    def __repr__(self) -> str:
        return f"<Nameplate sku_id={self.sku_id} palette={self.palette}>"

    def get_asset(self, animated: bool = False) -> Asset:
        """Returns the asset of the nameplate.

        Parameters
        ----------
        animated: :class:`bool`
            Whether to return the animated version of the asset, in webm version. Defaults to ``False``.
        """
        fn = "static.png" if not animated else "asset.webm"
        return Asset(
            state=self._state,
            url=f"{Asset.BASE}/assets/collectibles/{self._asset}{fn}",
            key=self._asset.split("/")[-1],
            animated=animated,
        )


__all__ = ("Nameplate", "NameplatePalette")
