from __future__ import annotations

from typing import TYPE_CHECKING

from ..components import Section as SectionComponent
from ..enums import ComponentType
from .item import Item

__all__ = ("InputText",)

if TYPE_CHECKING:
    from ..types.components import SectionComponent as SectionComponentPayload


class Section:
    """Represents a UI section.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items contained in this section, up to 3. Currently only supports :class:`~discord.ui.TextDisplay` and :class:`~discord.ui.Button`.
    accessory: Optional[:class:`Item`]
        This section's accessory. This is displayed in the top right of the section. Currently only supports :class:`~discord.ui.TextDisplay` and :class:`~discord.ui.Button`.
    """

    def __init__(self, *items: Item, accessory: Item = None):
        super().__init__()

        self.items = items
        self.accessory = accessory
        components = []

        self._underlying = SectionComponent._raw_construct(
            type=ComponentType.section,
            components=components,
            accessory=accessory,
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

    def add_button(
        self,
        label: str,
    ) -> None:
        """finish"""

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def to_component_dict(self) -> SectionComponentPayload:
        return self._underlying.to_dict()
