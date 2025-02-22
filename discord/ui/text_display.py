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
    """Represents a UI TextDisplay.

    .. versionadded:: 2.7

    Parameters
    ----------
    content: :class:`str`
        The text display's content.
    """

    def __init__(self, content: str):
        super().__init__()

        self.content = content

        self._underlying = TextDisplayComponent._raw_construct(
            type=ComponentType.text_display,
            id=None,
            content=content,
        )

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def to_component_dict(self) -> TextDisplayPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[T], component: TextDisplayComponent) -> T:
        return cls(component.content)

    callback = None
