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

from ..components import TextDisplay as TextDisplayComponent
from ..components import _component_factory
from ..enums import ComponentType
from .item import ModalItem, ViewItem

__all__ = ("TextDisplay",)

if TYPE_CHECKING:
    from ..types.components import TextDisplayComponent as TextDisplayComponentPayload
    from .core import ItemInterface
    from .modal import DesignerModal
    from .view import DesignerView


T = TypeVar("T", bound="TextDisplay")
V = TypeVar("V", bound="DesignerView", covariant=True)
M = TypeVar("M", bound="DesignerModal", covariant=True)


class TextDisplay(ViewItem[V], ModalItem[M]):
    """Represents a UI text display. A message can have up to 4000 characters across all :class:`TextDisplay` objects combined.

    .. versionadded:: 2.7

    Parameters
    ----------
    content: :class:`str`
        The text display's content, up to 4000 characters.
    id: Optional[:class:`int`]
        The text display's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "content",
        "id",
    )

    def __init__(
        self,
        content: str,
        id: int | None = None,
    ):
        super().__init__()

        self._underlying = self._generate_underlying(
            id=id,
            content=content,
        )

    def _generate_underlying(
        self,
        content: str | None = None,
        id: int | None = None,
    ) -> TextDisplayComponent:
        super()._generate_underlying(TextDisplayComponent)
        return TextDisplayComponent._raw_construct(
            type=ComponentType.text_display,
            id=id or self.id,
            content=content or self.content,
        )

    @property
    def content(self) -> str:
        """The text display's content."""
        return self.underlying.content

    @content.setter
    def content(self, value: str) -> None:
        self.underlying.content = value

    def to_component_dict(self) -> TextDisplayComponentPayload:
        return super().to_component_dict()

    def copy_text(self) -> str:
        """Returns the content of this text display. Equivalent to the `Copy Text` option on Discord clients."""
        return self.content

    @classmethod
    def from_component(cls: type[T], component: TextDisplayComponent) -> T:
        return cls(component.content, id=component.id)

    callback = None
