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

from typing import TYPE_CHECKING, TypeVar

from ..components import Separator as SeparatorComponent
from ..components import _component_factory
from ..enums import ComponentType, SeparatorSpacingSize
from .item import ViewItem

__all__ = ("Separator",)

if TYPE_CHECKING:
    from ..types.components import SeparatorComponent as SeparatorComponentPayload
    from .view import DesignerView


S = TypeVar("S", bound="Separator")
V = TypeVar("V", bound="DesignerView", covariant=True)


class Separator(ViewItem[V]):
    """Represents a UI Separator.

    .. versionadded:: 2.7

    Parameters
    ----------
    divider: :class:`bool`
        Whether the separator is a divider. Defaults to ``True``.
    spacing: :class:`~discord.SeparatorSpacingSize`
        The spacing size of the separator. Defaults to :attr:`~discord.SeparatorSpacingSize.small`.
    id: Optional[:class:`int`]
        The separator's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "divider",
        "spacing",
        "id",
    )

    def __init__(
        self,
        *,
        divider: bool = True,
        spacing: SeparatorSpacingSize = SeparatorSpacingSize.small,
        id: int | None = None,
    ):
        super().__init__()

        self._underlying = self._generate_underlying(
            id=id,
            divider=divider,
            spacing=spacing,
        )

    def _generate_underlying(
        self,
        divider: bool | None = None,
        spacing: SeparatorSpacingSize | None = None,
        id: int | None = None,
    ) -> SeparatorComponent:
        return SeparatorComponent._raw_construct(
            type=ComponentType.separator,
            id=id or self.id,
            divider=divider if divider is not None else self.divider,
            spacing=spacing,
        )

    @property
    def divider(self) -> bool:
        """Whether the separator is a divider. Defaults to ``True``."""
        return self.underlying.divider

    @divider.setter
    def divider(self, value: bool) -> None:
        self.underlying.divider = value

    @property
    def spacing(self) -> SeparatorSpacingSize:
        """The spacing size of the separator. Defaults to :attr:`~discord.SeparatorSpacingSize.small`."""
        return self.underlying.spacing

    @spacing.setter
    def spacing(self, value: SeparatorSpacingSize) -> None:
        self.underlying.spacing = value

    def to_component_dict(self) -> SeparatorComponentPayload:
        return super().to_component_dict()

    @classmethod
    def from_component(cls: type[S], component: SeparatorComponent) -> S:
        return cls(
            divider=component.divider, spacing=component.spacing, id=component.id
        )

    callback = None
