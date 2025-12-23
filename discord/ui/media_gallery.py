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

from ..components import MediaGallery as MediaGalleryComponent
from ..components import MediaGalleryItem
from ..enums import ComponentType
from .item import ViewItem

__all__ = ("MediaGallery",)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.components import MediaGalleryComponent as MediaGalleryComponentPayload
    from .view import DesignerView


M = TypeVar("M", bound="MediaGallery")
V = TypeVar("V", bound="DesignerView", covariant=True)


class MediaGallery(ViewItem[V]):
    """Represents a UI Media Gallery. Galleries may contain up to 10 :class:`MediaGalleryItem` objects.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`MediaGalleryItem`
        The initial items contained in this gallery, up to 10.
    id: Optional[:class:`int`]
        The gallery's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "items",
        "id",
    )

    def __init__(self, *items: MediaGalleryItem, id: int | None = None):
        super().__init__()

        self._underlying = self._generate_underlying(
            id=id, items=items
        )

    def _generate_underlying(self, id: int | None = None, items: list[MediaGalleryItem] | None = None) -> MediaGalleryComponent:
        return MediaGalleryComponent._raw_construct(
            type=ComponentType.media_gallery, id=id or self.id, items=[i for i in items] if items else []
        )

    @property
    def items(self):
        return self.underlying.items

    def append_item(self, item: MediaGalleryItem) -> Self:
        """Adds a :attr:`MediaGalleryItem` to the gallery.

        Parameters
        ----------
        item: :class:`MediaGalleryItem`
            The gallery item to add to the gallery.

        Raises
        ------
        TypeError
            A :class:`MediaGalleryItem` was not passed.
        ValueError
            Maximum number of items has been exceeded (10).
        """

        if len(self.items) >= 10:
            raise ValueError("maximum number of children exceeded")

        if not isinstance(item, MediaGalleryItem):
            raise TypeError(f"expected MediaGalleryItem not {item.__class__!r}")

        self.underlying.items.append(item)
        return self

    def add_item(
        self,
        url: str,
        *,
        description: str = None,
        spoiler: bool = False,
    ) -> Self:
        """Adds a new media item to the gallery.

        Parameters
        ----------
        url: :class:`str`
            The URL of the media item. This can either be an arbitrary URL or an ``attachment://`` URL.
        description: Optional[:class:`str`]
            The media item's description, up to 1024 characters.
        spoiler: Optional[:class:`bool`]
            Whether the media item has the spoiler overlay.

        Raises
        ------
        ValueError
            Maximum number of items has been exceeded (10).
        """

        if len(self.items) >= 10:
            raise ValueError("maximum number of items exceeded")

        item = MediaGalleryItem(url, description=description, spoiler=spoiler)

        return self.append_item(item)

    def to_component_dict(self) -> MediaGalleryComponentPayload:
        return super().to_component_dict()

    @classmethod
    def from_component(cls: type[M], component: MediaGalleryComponent) -> M:
        return cls(*component.items, id=component.id)

    callback = None
