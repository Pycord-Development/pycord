from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, ClassVar, TypeVar

from ..components import Section as SectionComponent
from ..components import _component_factory
from ..enums import ComponentType
from .item import Item, ItemCallbackType
from .text_display import TextDisplay

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

    def __init__(self, *items: Item, accessory: Item = None):
        super().__init__()

        self.items = []
        [i._underlying for i in items]
        self.accessory = None

        self._underlying = SectionComponent._raw_construct(
            type=ComponentType.section,
            id=None,
            components=[],
            accessory=None,
        )
        if func := self.__section_accessory_item__:
            item: Item = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            if self.view:
                item.callback = partial(func, self.view, item)
                setattr(self.view, func.__name__, item)
            else:
                item._tmp_func = func
            self.set_accessory(item)
        elif accessory:
            self.set_accessory(accessory)
        for i in items:
            self.add_item(i)

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
        self._underlying.components.append(item._underlying)

    def add_text(self, content: str) -> None:
        """Adds a :class:`TextDisplay` to the section.

        Parameters
        ----------
        content: :class:`str`
            The content of the TextDisplay

        Raises
        ------
        TypeError
            A :class:`str` was not passed.
        ValueError
            Maximum number of items has been exceeded (3).
        """

        if len(self.items) >= 3:
            raise ValueError("maximum number of children exceeded")

        text = TextDisplay(content)

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

        self.accessory = item
        self._underlying.accessory = item._underlying

    @Item.view.setter
    def view(self, value):
        self._view = value
        if self.accessory:
            if getattr(self.accessory, "_tmp_func", None):
                self.accessory.callback = partial(
                    self.accessory._tmp_func, self.view, self.accessory
                )
                setattr(self.view, self.accessory._tmp_func.__name__, self.accessory)
                delattr(self.accessory, "_tmp_func")
            self.accessory._view = value

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    @property
    def width(self) -> int:
        return 5

    def to_component_dict(self) -> SectionComponentPayload:
        return self._underlying.to_dict()

    @classmethod
    def from_component(cls: type[S], component: SectionComponent) -> S:
        from .view import _component_to_item

        items = [_component_to_item(c) for c in component.components]
        accessory = _component_to_item(component.accessory)
        return cls(*items, accessory=accessory)

    callback = None
