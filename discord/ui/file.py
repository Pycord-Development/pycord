from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from ..components import FileComponent, UnfurledMediaItem, _component_factory
from ..enums import ComponentType
from .item import Item

__all__ = ("File",)

if TYPE_CHECKING:
    from ..types.components import FileComponent as FileComponentPayload
    from .view import View


F = TypeVar("F", bound="File")
V = TypeVar("V", bound="View", covariant=True)


class File(Item[V]):
    """Represents a UI File.

    .. versionadded:: 2.7

    Parameters
    ----------
    """

    def __init__(self, url: str, *, spoiler: bool = False):
        super().__init__()

        file = UnfurledMediaItem(url)
        self._url = url
        self._spoiler: bool = spoiler

        self._underlying = FileComponent._raw_construct(
            type=ComponentType.file,
            id=None,
            file=file,
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
        """The URL of this file's media. This must be an ``attachment://`` URL that references a :class:`~discord.File`."""
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value
        self._underlying.file.url = value

    @property
    def spoiler(self) -> bool:
        """Whether the file is a spoiler. Defaults to ``False``."""
        return self._spoiler

    @spoiler.setter
    def spoiler(self, spoiler: bool) -> None:
        self._spoiler = spoiler
        self._underlying.spoiler = spoiler

    def to_component_dict(self) -> FileComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[F], component: FileComponent) -> F:
        return cls(
            component.file and component.file.url,
            spoiler=component.spoiler,
        )

    callback = None
