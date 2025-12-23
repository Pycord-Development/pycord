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

from ..components import Thumbnail as ThumbnailComponent
from ..components import UnfurledMediaItem, _component_factory
from ..enums import ComponentType
from .item import ViewItem

__all__ = ("Thumbnail",)

if TYPE_CHECKING:
    from ..types.components import ThumbnailComponent as ThumbnailComponentPayload
    from .view import DesignerView


T = TypeVar("T", bound="Thumbnail")
V = TypeVar("V", bound="DesignerView", covariant=True)


class Thumbnail(ViewItem[V]):
    """Represents a UI Thumbnail.

    .. versionadded:: 2.7

    Parameters
    ----------
    url: :class:`str`
        The url of the thumbnail. This can either be an arbitrary URL or an ``attachment://`` URL to work with local files.
    description: Optional[:class:`str`]
        The thumbnail's description, up to 1024 characters.
    spoiler: Optional[:class:`bool`]
        Whether the thumbnail has the spoiler overlay. Defaults to ``False``.
    id: Optional[:class:`int`]
        The thumbnail's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "url",
        "description",
        "spoiler",
        "id",
    )

    def __init__(
        self,
        url: str,
        *,
        description: str = None,
        spoiler: bool = False,
        id: int = None,
    ):
        super().__init__()

        media = UnfurledMediaItem(url)

        self._underlying = self._generate_underlying(
            id=id,
            media=media,
            description=description,
            spoiler=spoiler,
        )

    def _generate_underlying(
        self,
        media: UnfurledMediaItem | None = None,
        description: str | None = None,
        spoiler: bool | None = False,
        id: int | None = None,
    ) -> ThumbnailComponent:
        super()._generate_underlying(ThumbnailComponent)
        return ThumbnailComponent._raw_construct(
            type=ComponentType.thumbnail,
            id=id or self.id,
            media=media or self.media,
            description=description or self.description,
            spoiler=spoiler if spoiler is not None else self.spoiler,
        )

    @property
    def media(self) -> UnfurledMediaItem:
        """The thumbnail's unerlying media item."""
        return self.underlying.media

    @media.setter
    def url(self, value: UnfurledMediaItem) -> None:
        self.underlying.media = value

    @property
    def url(self) -> str:
        """The URL of this thumbnail's media. This can either be an arbitrary URL or an ``attachment://`` URL."""
        return self.underlying.media and self.underlying.media.url

    @url.setter
    def url(self, value: str) -> None:
        self.underlying.media.url = value

    @property
    def description(self) -> str | None:
        """The thumbnail's description, up to 1024 characters."""
        return self.underlying.description

    @description.setter
    def description(self, description: str | None) -> None:
        self.underlying.description = description

    @property
    def spoiler(self) -> bool:
        """Whether the thumbnail has the spoiler overlay. Defaults to ``False``."""

        return self.underlying.spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self.underlying.spoiler = spoiler

    def to_component_dict(self) -> ThumbnailComponentPayload:
        return super().to_component_dict()

    @classmethod
    def from_component(cls: type[T], component: ThumbnailComponent) -> T:
        return cls(
            component.media and component.media.url,
            description=component.description,
            spoiler=component.spoiler,
            id=component.id,
        )

    callback = None
