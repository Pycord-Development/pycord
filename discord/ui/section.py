"""
The MIT License (MIT)

Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, ClassVar, Iterator, TypeVar

from ..components import Section as SectionComponent
from ..components import _component_factory
from ..enums import ComponentType
from ..utils import find, get
from .button import Button
from .item import ItemCallbackType, ViewItem
from .text_display import TextDisplay
from .thumbnail import Thumbnail

__all__ = ("Section",)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.components import SectionComponent as SectionComponentPayload
    from .view import DesignerView


S = TypeVar("S", bound="Section")
V = TypeVar("V", bound="DesignerView", covariant=True)


class Section(ViewItem[V]):
    """Represents a UI section. Sections must have 1-3 (inclusive) items and an accessory set.

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`ViewItem`
        The initial items contained in this section, up to 3.
        Currently only supports :class:`~discord.ui.TextDisplay`.
        Sections must have at least 1 item before being sent.
    accessory: Optional[:class:`ViewItem`]
        The section's accessory. This is displayed in the top right of the section.
        Currently only supports :class:`~discord.ui.Button` and :class:`~discord.ui.Thumbnail`.
        Sections must have an accessory attached before being sent.
    id: Optional[:class:`int`]
        The section's ID.

    Attributes
    ----------
    items: List[:class:`ViewItem`]
        The list of items in this section.
    accessory: :class:`ViewItem`
        The section's accessory, displayed in the top right of the section.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "items",
        "accessory",
        "id",
    )

    __section_accessory_item__: ClassVar[ItemCallbackType] = []

    def __init_subclass__(cls) -> None:
        accessory: list[ItemCallbackType] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    accessory.append(member)

        cls.__section_accessory_item__ = accessory

    def __init__(
        self, *items: ViewItem, accessory: ViewItem = None, id: int | None = None
    ):
        super().__init__()

        self.items: list[ViewItem] = []
        self.accessory: ViewItem | None = None

        self._underlying = self._generate_underlying(
            id=id,
        )
        for func in self.__section_accessory_item__:
            item: ViewItem = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            item.callback = partial(func, self, item)
            self.set_accessory(item)
            setattr(self, func.__name__, item)
        if accessory:
            self.set_accessory(accessory)
        for i in items:
            self.add_item(i)

    def _add_component_from_item(self, item: ViewItem):
        self.underlying.components.append(item.underlying)

    def _set_components(self, items: list[ViewItem]):
        self.underlying.components.clear()
        for item in items:
            self._add_component_from_item(item)

    def _generate_underlying(self, id: int | None = None) -> SectionComponent:
        super()._generate_underlying(SectionComponent)
        section = SectionComponent._raw_construct(
            type=ComponentType.section,
            id=id or self.id,
            components=[],
            accessory=None,
        )
        for i in self.items:
            section.components.append(i._generate_underlying())
        if self.accessory:
            section.accessory = self.accessory._generate_underlying()
        return section

    def add_item(self, item: ViewItem) -> Self:
        """Adds an item to the section.

        Parameters
        ----------
        item: :class:`ViewItem`
            The item to add to the section.

        Raises
        ------
        TypeError
            An :class:`ViewItem` was not passed.
        ValueError
            Maximum number of items has been exceeded (3).
        """

        if len(self.items) >= 3:
            raise ValueError("maximum number of children exceeded")

        if not isinstance(item, ViewItem):
            raise TypeError(f"expected ViewItem not {item.__class__!r}")

        item.parent = self
        self.items.append(item)
        self._add_component_from_item(item)
        return self

    def remove_item(self, item: ViewItem | str | int) -> Self:
        """Removes an item from the section. If an :class:`int` or :class:`str` is passed,
        the item will be removed by Item ``id`` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`ViewItem`, :class:`int`, :class:`str`]
            The item, item ``id``, or item ``custom_id`` to remove from the section.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            if item is self.accessory:
                self.accessory = None
            else:
                self.items.remove(item)
            item.parent = None
        except ValueError:
            pass
        return self

    def replace_item(
        self, original_item: ViewItem | str | int, new_item: ViewItem
    ) -> Self:
        """Directly replace an item in this section.
        If an :class:`int` is provided, the item will be replaced by ``id``, otherwise by  ``custom_id``.

        Parameters
        ----------
        original_item: Union[:class:`ViewItem`, :class:`int`, :class:`str`]
            The item, item ``id``, or item ``custom_id`` to replace in the section.
        new_item: :class:`ViewItem`
            The new item to insert into the section.
        """

        if not isinstance(new_item, ViewItem):
            raise TypeError(f"expected ViewItem not {new_item.__class__!r}")

        if isinstance(original_item, (str, int)):
            original_item = self.get_item(original_item)
        if not original_item:
            raise ValueError(f"Could not find original_item in section.")
        try:
            if original_item is self.accessory:
                self.accessory = new_item
            else:
                i = self.items.index(original_item)
                self.items[i] = new_item
            original_item.parent = None
            new_item.parent = self
        except ValueError:
            raise ValueError(f"Could not find original_item in section.")
        return self

    def get_item(self, id: int | str) -> ViewItem | None:
        """Get an item from this section. Alias for `utils.get(section.walk_items(), ...)`.
        If an ``int`` is provided, it will be retrieved by ``id``, otherwise it will check the accessory's ``custom_id``.

        Parameters
        ----------
        id: Union[:class:`str`, :class:`int`]
            The id or custom_id of the item to get.

        Returns
        -------
        Optional[:class:`ViewItem`]
            The item with the matching ``id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        if self.accessory and id == getattr(self.accessory, attr, None):
            return self.accessory
        child = find(lambda i: getattr(i, attr, None) == id, self.items)
        return child

    def add_text(self, content: str, *, id: int | None = None) -> Self:
        """Adds a :class:`TextDisplay` to the section.

        Parameters
        ----------
        content: :class:`str`
            The content of the text display.
        id: Optional[:class:`int`]
            The text display's ID.

        Raises
        ------
        ValueError
            Maximum number of items has been exceeded (3).
        """

        if len(self.items) >= 3:
            raise ValueError("maximum number of children exceeded")

        text = TextDisplay(content, id=id)

        return self.add_item(text)

    def set_accessory(self, item: ViewItem) -> Self:
        """Set an item as the section's :attr:`accessory`.

        Parameters
        ----------
        item: :class:`ViewItem`
            The item to set as accessory.
            Currently only supports :class:`~discord.ui.Button` and :class:`~discord.ui.Thumbnail`.

        Raises
        ------
        TypeError
            An :class:`ViewItem` was not passed.
        """

        if not isinstance(item, ViewItem):
            raise TypeError(f"expected ViewItem not {item.__class__!r}")

        item.parent = self

        self.accessory = item
        self.underlying.accessory = item._generate_underlying()
        return self

    def set_thumbnail(
        self,
        url: str,
        *,
        description: str | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ) -> Self:
        """Sets a :class:`Thumbnail` with the provided URL as the section's :attr:`accessory`.

        Parameters
        ----------
        url: :class:`str`
            The url of the thumbnail.
        description: Optional[:class:`str`]
            The thumbnail's description, up to 1024 characters.
        spoiler: Optional[:class:`bool`]
            Whether the thumbnail has the spoiler overlay. Defaults to ``False``.
        id: Optional[:class:`int`]
            The thumbnail's ID.
        """

        thumbnail = Thumbnail(url, description=description, spoiler=spoiler, id=id)

        return self.set_accessory(thumbnail)

    def copy_text(self) -> str:
        """Returns the text of all :class:`~discord.ui.TextDisplay` items in this section.
        Equivalent to the `Copy Text` option on Discord clients.
        """
        return "\n".join(t for i in self.items if (t := i.copy_text()))

    def is_dispatchable(self) -> bool:
        return self.accessory and self.accessory.is_dispatchable()

    def is_persistent(self) -> bool:
        if not isinstance(self.accessory, Button):
            return True
        return self.accessory.is_persistent()

    def refresh_component(self, component: SectionComponent) -> None:
        self.underlying = component
        for x, y in zip(self.items, component.components):
            x.refresh_component(y)
        if self.accessory and component.accessory:
            self.accessory.refresh_component(component.accessory)

    def disable_all_items(self, *, exclusions: list[ViewItem] | None = None) -> Self:
        """
        Disables all buttons and select menus in the section.
        At the moment, this only disables :attr:`accessory` if it is a button.

        Parameters
        ----------
        exclusions: Optional[List[:class:`ViewItem`]]
            A list of items in `self.items` to not disable from the view.
        """
        for item in self.walk_items():
            if hasattr(item, "disabled") and (
                exclusions is None or item not in exclusions
            ):
                item.disabled = True
        return self

    def enable_all_items(self, *, exclusions: list[ViewItem] | None = None) -> Self:
        """
        Enables all buttons and select menus in the section.
        At the moment, this only enables :attr:`accessory` if it is a button.

        Parameters
        ----------
        exclusions: Optional[List[:class:`ViewItem`]]
            A list of items in `self.items` to not enable from the view.
        """
        for item in self.walk_items():
            if hasattr(item, "disabled") and (
                exclusions is None or item not in exclusions
            ):
                item.disabled = False
        return self

    def walk_items(self) -> Iterator[ViewItem]:
        r = self.items
        if self.accessory:
            yield from r + [self.accessory]
        else:
            yield from r

    def to_component_dict(self) -> SectionComponentPayload:
        self._underlying = self._generate_underlying()
        return super().to_component_dict()

    @classmethod
    def from_component(cls: type[S], component: SectionComponent) -> S:
        from .view import _component_to_item

        items = [_component_to_item(c) for c in component.components]
        accessory = _component_to_item(component.accessory)
        return cls(*items, accessory=accessory, id=component.id)

    callback = None
