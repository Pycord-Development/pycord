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

        self._underlying = ThumbnailComponent._raw_construct(
            type=ComponentType.thumbnail,
            id=id,
            media=media,
            description=description,
            spoiler=spoiler,
        )

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def url(self) -> str:
        """The URL of this thumbnail's media. This can either be an arbitrary URL or an ``attachment://`` URL."""
        return self._underlying.media and self._underlying.media.url

    @url.setter
    def url(self, value: str) -> None:
        self._underlying.media.url = value

    @property
    def description(self) -> str | None:
        """The thumbnail's description, up to 1024 characters."""
        return self._underlying.description

    @description.setter
    def description(self, description: str | None) -> None:
        self._underlying.description = description

    @property
    def spoiler(self) -> bool:
        """Whether the thumbnail has the spoiler overlay. Defaults to ``False``."""

        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self._underlying.spoiler = spoiler

    def to_component_dict(self) -> ThumbnailComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[T], component: ThumbnailComponent) -> T:
        return cls(
            component.media and component.media.url,
            description=component.description,
            spoiler=component.spoiler,
            id=component.id,
        )

    callback = None
