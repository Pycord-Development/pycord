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
from urllib.parse import urlparse

from ..components import FileComponent, UnfurledMediaItem, _component_factory
from ..enums import ComponentType
from .item import ViewItem

__all__ = ("File",)

if TYPE_CHECKING:
    from ..types.components import FileComponent as FileComponentPayload
    from .view import DesignerView


F = TypeVar("F", bound="File")
V = TypeVar("V", bound="DesignerView", covariant=True)


class File(ViewItem[V]):
    """Represents a UI File.

    .. note::
        This component does not show media previews. Use :class:`MediaGallery` for previews instead.

    .. versionadded:: 2.7

    Parameters
    ----------
    url: :class:`str`
        The URL of this file. This must be an ``attachment://`` URL referring to a local file used with :class:`~discord.File`.
    spoiler: Optional[:class:`bool`]
        Whether this file has the spoiler overlay.
    id: Optional[:class:`int`]
        The file component's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "file",
        "spoiler",
        "id",
    )

    def __init__(self, url: str, *, spoiler: bool = False, id: int | None = None):
        super().__init__()

        file = UnfurledMediaItem(url)

        self._underlying = self._generate_underlying(
            id=id,
            file=file,
            spoiler=spoiler,
        )

    def _generate_underlying(
        self, file: UnfurledMediaItem | None = None, spoiler: bool | None = None, id: int | None = None
    ) -> FileComponent:
        return FileComponent._raw_construct(
            type=ComponentType.file,
            id=id or self.id,
            file=file or self.file,
            spoiler=spoiler if spoiler is not None else self.spoiler,
        )

    @property
    def file(self) -> UnfurledMediaItem:
        """The file's unerlying media item."""
        return self.underlying.file

    @file.setter
    def url(self, value: UnfurledMediaItem) -> None:
        self.underlying.file = value

    @property
    def url(self) -> str:
        """The URL of this file's underlying media. This must be an ``attachment://`` URL that references a :class:`~discord.File`."""
        return self.underlying.file and self.underlying.file.url

    @url.setter
    def url(self, value: str) -> None:
        self.underlying.file.url = value

    @property
    def spoiler(self) -> bool:
        """Whether the file has the spoiler overlay. Defaults to ``False``."""
        return self.underlying.spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self.underlying.spoiler = spoiler

    @property
    def name(self) -> str:
        """The name of this file, if provided by Discord."""
        return self.underlying.name

    @property
    def size(self) -> int:
        """The size of this file in bytes, if provided by Discord."""
        return self.underlying.size

    def refresh_component(self, component: FileComponent) -> None:
        original = self.underlying.file
        component.file._static_url = original._static_url
        self.underlying = component

    def to_component_dict(self) -> FileComponentPayload:
        return super().to_component_dict()

    @classmethod
    def from_component(cls: type[F], component: FileComponent) -> F:
        url = component.file and component.file.url
        if not url.startswith("attachment://"):
            url = "attachment://" + urlparse(url).path.rsplit("/", 1)[-1]
        return cls(
            url,
            spoiler=component.spoiler,
            id=component.id,
        )

    callback = None
