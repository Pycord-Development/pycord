from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from ..components import Separator as SeparatorComponent
from ..components import _component_factory
from ..enums import ComponentType, SeparatorSpacingSize
from .item import ViewItem

__all__ = ("Separator",)

if TYPE_CHECKING:
    from ..types.components import SeparatorComponent as SeparatorComponentPayload
    from .view import DesignerView


S = TypeVar("S", bound="Separator")
V = TypeVar("V", bound="DesignerView", covariant=True)


class Separator(ViewItem[V]):
    """Represents a UI Separator.

    .. versionadded:: 2.7

    Parameters
    ----------
    divider: :class:`bool`
        Whether the separator is a divider. Defaults to ``True``.
    spacing: :class:`~discord.SeparatorSpacingSize`
        The spacing size of the separator. Defaults to :attr:`~discord.SeparatorSpacingSize.small`.
    id: Optional[:class:`int`]
        The separator's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "divider",
        "spacing",
        "id",
    )

    def __init__(
        self,
        *,
        divider: bool = True,
        spacing: SeparatorSpacingSize = SeparatorSpacingSize.small,
        id: int | None = None,
    ):
        super().__init__()

        self._underlying = SeparatorComponent._raw_construct(
            type=ComponentType.separator,
            id=id,
            divider=divider,
            spacing=spacing,
        )

    @property
    def divider(self) -> bool:
        """Whether the separator is a divider. Defaults to ``True``."""
        return self._underlying.divider

    @divider.setter
    def divider(self, value: bool) -> None:
        self._underlying.divider = value

    @property
    def spacing(self) -> SeparatorSpacingSize:
        """The spacing size of the separator. Defaults to :attr:`~discord.SeparatorSpacingSize.small`."""
        return self._underlying.spacing

    @spacing.setter
    def spacing(self, value: SeparatorSpacingSize) -> None:
        self._underlying.spacing = value

    def to_component_dict(self) -> SeparatorComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[S], component: SeparatorComponent) -> S:
        return cls(
            divider=component.divider, spacing=component.spacing, id=component.id
        )

    callback = None
