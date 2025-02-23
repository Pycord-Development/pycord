from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from ..components import Thumbnail as ThumbnailComponent
from ..components import UnfurledMediaItem, _component_factory
from ..enums import ComponentType
from .item import Item

__all__ = ("Thumbnail",)

if TYPE_CHECKING:
    from ..types.components import ThumbnailComponent as ThumbnailComponentPayload
    from .view import View


T = TypeVar("T", bound="Thumbnail")
V = TypeVar("V", bound="View", covariant=True)


class Thumbnail(Item[V]):
    """Represents a UI Thumbnail.

    .. versionadded:: 2.7

    Parameters
    ----------
    """

    def __init__(self, url: str, *, description: str = None, spoiler: bool = False):
        super().__init__()

        media = UnfurledMediaItem(url)
        self._url = url
        self._description: str | None = description
        self._spoiler: bool = spoiler

        self._underlying = ThumbnailComponent._raw_construct(
            type=ComponentType.thumbnail,
            id=None,
            media=media,
            description=description,
            spoiler=spoiler,
        )

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def width(self) -> int:
        return 5

    @property
    def url(self) -> str:
        """The URL of this thumbnail's media. This can either be an arbitrary URL or an ``attachment://`` URL."""
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value
        self._underlying.media.url = value

    @property
    def description(self) -> str | None:
        """The thumbnail's description, up to 1024 characters."""
        return self._description

    @description.setter
    def description(self, description: str | None) -> None:
        self._description = description
        self._underlying.description = description

    @property
    def spoiler(self) -> bool:
        """Whether the thumbnail is a spoiler. Defaults to ``False``."""
        return self.spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self._spoiler = spoiler
        self._underlying.spoiler = spoiler

    def to_component_dict(self) -> ThumbnailComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[T], component: ThumbnailComponent) -> T:
        return cls(
            component.media and component.media.url,
            description=component.description,
            spoiler=component.spoiler,
        )

    callback = None
