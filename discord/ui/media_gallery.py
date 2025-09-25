from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from ..components import MediaGallery as MediaGalleryComponent
from ..components import MediaGalleryItem
from ..enums import ComponentType
from .item import Item

__all__ = ("MediaGallery",)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.components import MediaGalleryComponent as MediaGalleryComponentPayload
    from .view import DesignerView


M = TypeVar("M", bound="MediaGallery")
V = TypeVar("V", bound="DesignerView", covariant=True)


class MediaGallery(Item[V]):
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

        self._underlying = MediaGalleryComponent._raw_construct(
            type=ComponentType.media_gallery, id=id, items=[i for i in items]
        )

    @property
    def items(self):
        return self._underlying.items

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

        self._underlying.items.append(item)
        return self

    def add_item(
        self,
        url: str,
        *,
        description: str = None,
        spoiler: bool = False,
    ) -> None:
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

    @Item.view.setter
    def view(self, value):
        self._view = value

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def to_component_dict(self) -> MediaGalleryComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[M], component: MediaGalleryComponent) -> M:
        return cls(*component.items, id=component.id)

    callback = None
