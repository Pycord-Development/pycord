from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from ..components import Separator as SeparatorComponent
from ..components import _component_factory
from ..enums import ComponentType, SeparatorSpacingSize
from .item import Item

__all__ = ("Separator",)

if TYPE_CHECKING:
    from ..types.components import SeparatorComponent as SeparatorComponentPayload
    from .view import View


S = TypeVar("S", bound="Separator")
V = TypeVar("V", bound="View", covariant=True)


class Separator(Item[V]):
    """Represents a UI Separator.

    .. versionadded:: 2.7

    Parameters
    ----------
    divider: :class:`bool`
        Whether the separator is a divider. Defaults to ``True``.
    spacing: :class:`~discord.SeparatorSpacingSize`
        The spacing size of the separator. Defaults to :attr:`~discord.SeparatorSpacingSize.small`.
    """

    def __init__(
        self,
        *,
        divider: bool = True,
        spacing: SeparatorSpacingSize = SeparatorSpacingSize.small,
    ):
        super().__init__()

        self.divider = divider
        self.spacing = spacing

        self._underlying = SeparatorComponent._raw_construct(
            type=ComponentType.text_display,
            id=None,
            divider=divider,
            spacing=spacing,
        )

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def width(self) -> int:
        return 5

    def to_component_dict(self) -> SeparatorComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[S], component: SeparatorComponent) -> S:
        return cls(component.content)

    callback = None
