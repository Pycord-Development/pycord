from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from ..components import Section as SectionComponent
from ..components import _component_factory
from ..enums import ComponentType
from .item import Item

__all__ = ("Section",)

if TYPE_CHECKING:
    from ..types.components import SectionComponent as SectionComponentPayload
    from .view import View


S = TypeVar("S", bound="Section")
V = TypeVar("V", bound="View", covariant=True)


class Section(Item[V]):
    """Represents a UI section.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items contained in this section, up to 3. Currently only supports :class:`~discord.ui.TextDisplay`.
    accessory: Optional[:class:`Item`]
        This section's accessory. This is displayed in the top right of the section. Currently only supports :class:`~discord.ui.Thumbnail` and :class:`~discord.ui.Button`.
    """

    def __init__(self, *items: Item, accessory: Item = None):
        super().__init__()

        self.items = items
        self.accessory = accessory
        components = [i._underlying for i in items]

        self._underlying = SectionComponent._raw_construct(
            type=ComponentType.section,
            id=None,
            components=components,
            accessory=accessory and accessory._underlying,
        )

    def add_item(self, item: Item) -> None:
        """Adds an item to the section.

        Parameters
        ----------
        item: :class:`Item`
            The item to add to the section.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        ValueError
            Maximum number of items has been exceeded (10).
        """

        if len(self.items) >= 3:
            raise ValueError("maximum number of children exceeded")

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")

        self.items.append(item)

    def add_text(self, content: str) -> None:
        """Adds a :class:`TextDisplay` to the section.

        Parameters
        ----------
        content: :class:`str`
            The content of the TextDisplay

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        ValueError
            Maximum number of items has been exceeded (3).
        """

        if len(self.items) >= 3:
            raise ValueError("maximum number of children exceeded")

        text = ...

        self.items.append(text)

    def set_accessory(self, item: Item) -> None:
        """Set an item as the section's :attr:`accessory`.

        Parameters
        ----------
        item: :class:`Item`
            The item to set as accessory. Currently only supports :class:`~discord.ui.Thumbnail` and :class:`~discord.ui.Button`.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        """

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")

        self.accessory = item

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def to_component_dict(self) -> SectionComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[S], component: SectionComponent) -> S:
        from .view import _component_to_item

        items = [_component_to_item(c) for c in component.components]
        accessory = _component_to_item(component.accessory)
        return cls(*items, accessory=accessory)

    callback = None
