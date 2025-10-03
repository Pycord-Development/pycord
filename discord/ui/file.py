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

        self.file = UnfurledMediaItem(url)

        self._underlying = FileComponent._raw_construct(
            type=ComponentType.file,
            id=id,
            file=self.file,
            spoiler=spoiler,
        )

    @property
    def url(self) -> str:
        """The URL of this file's media. This must be an ``attachment://`` URL that references a :class:`~discord.File`."""
        return self._underlying.file and self._underlying.file.url

    @url.setter
    def url(self, value: str) -> None:
        self._underlying.file.url = value

    @property
    def spoiler(self) -> bool:
        """Whether the file has the spoiler overlay. Defaults to ``False``."""
        return self._underlying.spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self._underlying.spoiler = spoiler

    @property
    def name(self) -> str:
        """The name of this file, if provided by Discord."""
        return self._underlying.name

    @property
    def size(self) -> int:
        """The size of this file in bytes, if provided by Discord."""
        return self._underlying.size

    def refresh_component(self, component: FileComponent) -> None:
        original = self._underlying.file
        component.file._static_url = original._static_url
        self._underlying = component

    def to_component_dict(self) -> FileComponentPayload:
        return self._underlying.to_dict()

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
