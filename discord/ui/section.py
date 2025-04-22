from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, ClassVar, TypeVar

from ..components import Section as SectionComponent
from ..components import _component_factory
from ..enums import ComponentType
from ..utils import get
from .item import Item, ItemCallbackType
from .text_display import TextDisplay
from .thumbnail import Thumbnail

__all__ = ("Section",)

if TYPE_CHECKING:
    from ..types.components import SectionComponent as SectionComponentPayload
    from .view import View


S = TypeVar("S", bound="Section")
V = TypeVar("V", bound="View", covariant=True)


class Section(Item[V]):
    """Represents a UI section. Sections must have 1-3 items and an accessory set.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`Item`
        The initial items contained in this section, up to 3.
        Currently only supports :class:`~discord.ui.TextDisplay`.
    accessory: Optional[:class:`Item`]
        The section's accessory. This is displayed in the top right of the section.
        Currently only supports :class:`~discord.ui.Button` and :class:`~discord.ui.Thumbnail`.
    """

    __section_accessory_item__: ClassVar[ItemCallbackType] = None

    def __init_subclass__(cls) -> None:
        accessory: ItemCallbackType = None
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    accessory = member

        cls.__section_accessory_item__ = accessory

    def __init__(self, *items: Item, accessory: Item = None, id: int | None = None):
        super().__init__()

        self.items: list[Item] = []
        self.accessory: Item | None = None

        self._underlying = SectionComponent._raw_construct(
            type=ComponentType.section,
            id=id,
            components=[],
            accessory=None,
        )
        if func := self.__section_accessory_item__:
            item: Item = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            item.callback = partial(func, self, item)
            self.set_accessory(item)
            setattr(self, func.__name__, item)
        elif accessory:
            self.set_accessory(accessory)
        for i in items:
            self.add_item(i)

    def _add_component_from_item(self, item: Item):
        self._underlying.components.append(item._underlying)

    def _set_components(self, items: list[Item]):
        self._underlying.components.clear()
        for item in items:
            self._add_component_from_item(item)

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
        self._add_component_from_item(item)

    def get_item(self, id: int) -> Item | None:
        """Get an item from this section. Alias for `utils.get(section.items, id=id)`.

        Parameters
        ----------
        id: :class:`int`
            The id of the item to get

        Returns
        -------
        Optional[:class:`Item`]
            The item with the matching ``id`` if it exists.
        """
        if not id:
            return None
        if self.accessory and self.accessory.id == id:
            return self.accessory
        return get(self.items, id=id)

    def add_text(self, content: str, *, id: int | None = None) -> None:
        """Adds a :class:`TextDisplay` to the section.

        Parameters
        ----------
        content: :class:`str`
            The content of the text display.
        id: Optiona[:class:`int`]
            The text display's ID.

        Raises
        ------
        ValueError
            Maximum number of items has been exceeded (3).
        """

        if len(self.items) >= 3:
            raise ValueError("maximum number of children exceeded")

        text = TextDisplay(content, id=id)

        self.add_item(text)

    def set_accessory(self, item: Item) -> None:
        """Set an item as the section's :attr:`accessory`.

        Parameters
        ----------
        item: :class:`Item`
            The item to set as accessory.
            Currently only supports :class:`~discord.ui.Button` and :class:`~discord.ui.Thumbnail`.

        Raises
        ------
        TypeError
            An :class:`Item` was not passed.
        """

        if not isinstance(item, Item):
            raise TypeError(f"expected Item not {item.__class__!r}")
        if self.view:
            item._view = self.view

        self.accessory = item
        self._underlying.accessory = item._underlying

    def set_thumbnail(self, url: str, *, id: int | None = None) -> None:
        """Set a :class:`Thumbnail` with the provided url as the section's :attr:`accessory`.

        Parameters
        ----------
        url: :class:`str`
            The url of the thumbnail.
        id: Optiona[:class:`int`]
            The thumbnail's ID.
        """

        thumbnail = Thumbnail(url, id=id)

        self.set_accessory(thumbnail)

    @Item.view.setter
    def view(self, value):
        self._view = value
        if self.accessory:
            self.accessory._view = value

    def copy_text(self) -> str:
        """Returns the text of all :class:`~discord.ui.TextDisplay` items in this section. Equivalent to the `Copy Text` option on Discord clients."""
        return "\n".join(i.copy_text() for i in self.items)

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def width(self) -> int:
        return 5

    def to_component_dict(self) -> SectionComponentPayload:
        self._set_components(self.items)
        self.set_accessory(self.accessory)
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[S], component: SectionComponent) -> S:
        from .view import _component_to_item

        items = [_component_to_item(c) for c in component.components]
        accessory = _component_to_item(component.accessory)
        return cls(*items, accessory=accessory, id=component.id)

    callback = None
