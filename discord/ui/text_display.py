from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from ..components import TextDisplay as TextDisplayComponent
from ..components import _component_factory
from ..enums import ComponentType
from .item import Item

__all__ = ("TextDisplay",)

if TYPE_CHECKING:
    from ..types.components import TextDisplayComponent as TextDisplayComponentPayload
    from .view import View


T = TypeVar("T", bound="TextDisplay")
V = TypeVar("V", bound="View", covariant=True)


class TextDisplay(Item[V]):
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

        self._underlying = TextDisplayComponent._raw_construct(
            type=ComponentType.text_display,
            id=id,
            content=content,
        )

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def content(self) -> str:
        """The text display's content."""
        return self._underlying.content

    @content.setter
    def content(self, value: str) -> None:
        self._underlying.content = value

    @property
    def width(self) -> int:
        return 5

    def to_component_dict(self) -> TextDisplayComponentPayload:
        return self._underlying.to_dict()

    def copy_text(self) -> str:
        """Returns the content of this text display. Equivalent to the `Copy Text` option on Discord clients."""
        return self.content

    @classmethod
    def from_component(cls: type[T], component: TextDisplayComponent) -> T:
        return cls(component.content, id=component.id)

    callback = None
