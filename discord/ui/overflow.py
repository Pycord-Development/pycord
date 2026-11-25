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

import inspect
import os
from collections.abc import Callable, Iterator
from functools import partial
from typing import TYPE_CHECKING, ClassVar, TypeVar

from discord.utils import find

from ..components import MenuActionItem as MenuActionItemComponent
from ..components import OverflowMenu as OverflowMenuComponent
from ..components import OverflowMenuGroup as OverflowMenuGroupComponent
from ..emoji import AppEmoji, GuildEmoji
from ..enums import ComponentType, MenuActionItemStyle
from ..partial_emoji import PartialEmoji, _EmojiTag
from .item import ItemCallbackType, ViewItem

__all__ = ("MenuActionItem", "OverflowMenu", "OverflowMenuGroup", "action_item")

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.components import (
        MenuActionItemComponent as MenuActionItemComponentPayload,
    )
    from ..types.components import OverflowMenuComponent as OverflowMenuComponentPayload
    from ..types.components import (
        OverflowMenuGroup as OverflowMenuGroupComponentPayload,
    )
    from .view import DesignerView


V_co = TypeVar("V_co", bound="DesignerView", covariant=True)


class OverflowMenu(ViewItem[V_co]):
    """Represents a UI Overflow Menu. 
    
    .. note::
    
        Overflow menus only allow for 8 :class:`MenuActionItem`s across all groups.

    .. versionadded:: 2.9

    Parameters
    ----------
    *groups: :class:`~discord.ui.OverflowMenuGroup`
        The groups within this overflow menu.
    id: :class:`int` | :obj:`None`
        The overflow menu's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "groups",
        "id",
    )

    def __init__(self, *groups: OverflowMenuGroup, id: int | None = None):
        if len(groups) > 8:
            raise ValueError("cannot have more than 8 groups")
        super().__init__()

        self.groups: list[OverflowMenuGroup] = []

        self._underlying: OverflowMenuComponent = self._generate_underlying(id=id)
        for g in groups:
            self.add_group(g)

    def _generate_underlying(self, id: int | None = None) -> OverflowMenuComponent:
        super()._generate_underlying(OverflowMenuComponent)
        overflow = OverflowMenuComponent._raw_construct(
            type=ComponentType.overflow_menu,
            id=id or self.id,
            groups=[],
        )
        for group in self.groups:
            overflow.groups.append(group._generate_underlying())
        return overflow

    def _add_group_from_item(self, item: OverflowMenuGroup):
        self.underlying.groups.append(item._generate_underlying())

    def _set_groups(self, groups: list[OverflowMenuGroup]):
        self.underlying.groups.clear()
        for group in groups:
            self._add_group_from_item(group)

    def add_group(self, group: OverflowMenuGroup) -> Self:
        """Adds an :class:`~discord.ui.OverflowMenuGroup` to the overflow menu.

        Parameters
        ----------
        group: :class:`~discord.ui.OverflowMenuGroup`
            The gallery item to add to the gallery.

        Raises
        ------
        TypeError
            A :class:`~discord.ui.OverflowMenuGroup` was not passed.
        """

        if not isinstance(group, OverflowMenuGroup):
            raise TypeError(f"expected OverflowMenuGroup not {group.__class__!r}")

        if len(self.groups) >= 8:
            raise ValueError("cannot have more than 8 groups")

        group.parent = self

        self.groups.append(group)
        self._add_group_from_item(group)
        return self

    def remove_item(self, item: OverflowMenuGroup | MenuActionItem | str | int) -> Self:
        """Removes an item from the overflow. If an int or str is passed, it will remove by Item :attr:`id` or ``custom_id`` respectively.

        Parameters
        ----------
        group: :class:`discord.ui.OverflowMenuGroup` | :class:`discord.ui.MenuActionItem` | :class:`int` | :class:`str`
            The item, ``id``, or item ``custom_id`` to remove from the overflow.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            if item.parent is self:
                self.groups.remove(item)
                item.parent = None
            else:
                item.parent.remove_item(item)
        except ValueError:
            pass
        return self

    def get_item(self, id: str | int) -> OverflowMenuGroup | MenuActionItem | None:
        """Get an item from this overflow. Roughly equivalent to `utils.get(overflow.groups, ...)`.
        If an ``int`` is provided, the item will be retrieved by ``id``, otherwise by ``custom_id``.
        This method will also search for nested items.

        Parameters
        ----------
        id: :class:`str` | :class:`int`
            The id or custom_id of the item to get.

        Returns
        -------
        :class:`discord.ui.OverflowMenuGroup` | :class:`discord.ui.MenuActionItem` | :obj:`None`
            The item with the matching ``id`` or ``custom_id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        child = find(lambda i: getattr(i, attr, None) == id, self.groups)
        if not child:
            for g in self.groups:
                if child := g.get_item(id):
                    return child
        return child

    def is_dispatchable(self) -> bool:
        return any(group.is_dispatchable() for group in self.groups)

    def is_persistent(self) -> bool:
        return all(group.is_persistent() for group in self.groups)

    def refresh_component(self, component: OverflowMenuComponent) -> None:
        self.underlying = component
        for i, y in enumerate(component.groups):
            x = self.groups[i]
            x.refresh_component(y)

    def walk_items(self) -> Iterator[OverflowMenuGroup | MenuActionItem]:
        for group in self.groups:
            yield from group.walk_items()

    def to_component_dict(self) -> OverflowMenuComponentPayload:
        self._underlying = self._generate_underlying()
        return super().to_component_dict()

    @classmethod
    def from_component(cls, component: OverflowMenuComponent) -> Self:
        groups: list[OverflowMenuGroup] = [OverflowMenuGroup.from_component(g) for g in component.groups]
        return cls(
            *groups,
            id=component.id,
        )

    callback = None


# this is not an actual component (it has no type), but stores actual components with callbacks
# so we can't just use the discord model
# but it is made to closely mimic an item
class OverflowMenuGroup:
    """Represents a UI Overflow Menu group.

    .. versionadded:: 2.9

    Parameters
    ----------
    *components: :class:`~discord.ui.MenuActionItem`
        The items within this group.
    label: :class:`str` | :obj:`None`
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "components",
        "label",
    )
    __row_children_items__: ClassVar[list[ItemCallbackType]] = []

    def __init_subclass__(cls) -> None:
        children: list[ItemCallbackType] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    children.append(member)

        cls.__row_children_items__ = children

    def __init__(self, *components: MenuActionItem, label: str | None = None):
        if len(self.__row_children_items__) + len(components) > 8:
            raise ValueError("cannot have more than 8 components")
        super().__init__()

        self.components: list[MenuActionItem] = []
        self.parent: OverflowMenu | DesignerView | None = None

        self._underlying: OverflowMenuGroupComponent = self._generate_underlying(
            label=label
        )

        for func in self.__row_children_items__:
            item: MenuActionItem = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            item.callback = partial(func, self, item)
            self.add_item(item)
            setattr(self, func.__name__, item)
        for c in components:
            self.add_item(c)

    def __repr__(self) -> str:
        attrs = " ".join(
            f"{key}={getattr(self, key)!r}" for key in self.__item_repr_attributes__
        )
        return f"<{self.__class__.__name__} {attrs}>"

    @property
    def label(self) -> str | None:
        """The label of the group, if available."""
        return self.underlying.label

    @label.setter
    def label(self, value: str | None):
        self.underlying.label = str(value) if value is not None else value

    def add_item(self, item: MenuActionItem) -> Self:
        """Adds an :class:`~discord.ui.MenuActionItem` to the overflow group.

        Parameters
        ----------
        item: :class:`~discord.ui.MenuActionItem`
            The gallery item to add to the gallery.

        Raises
        ------
        TypeError
            A :class:`~discord.ui.MenuActionItem` was not passed.
        """

        if not isinstance(item, MenuActionItem):
            raise TypeError(f"expected MenuActionItem not {item.__class__!r}")

        if len(self.components) >= 8:
            raise ValueError("cannot have more than 8 components")

        item.parent = self

        self.components.append(item)
        self._add_component_from_item(item)
        return self

    def remove_item(self, item: MenuActionItem | str | int) -> Self:
        """Removes an item from the group. If an int or str is passed, it will remove by Item :attr:`id` or ``custom_id`` respectively.

        Parameters
        ----------
        group: :class:`discord.ui.MenuActionItem` | :class:`int` | :class:`str`
            The item, ``id``, or item ``custom_id`` to remove from the overflow.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            self.components.remove(item)
        except ValueError:
            pass
        return self

    def get_item(self, id: str | int) -> MenuActionItem | None:
        """Get an item from this group. Roughly equivalent to `utils.get(group.components, ...)`.
        If an ``int`` is provided, the item will be retrieved by ``id``, otherwise by ``custom_id``.

        Parameters
        ----------
        id: :class:`str` | :class:`int`
            The id or custom_id of the item to get.

        Returns
        -------
        :class:`discord.ui.MenuActionItem` | :obj:`None`
            The item with the matching ``id`` or ``custom_id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        child = find(lambda i: getattr(i, attr, None) == id, self.components)
        return child

    def _generate_underlying(
        self, label: str | None = None
    ) -> OverflowMenuGroupComponent:
        components = []
        for component in self.components:
            components.append(component._generate_underlying())
        group = OverflowMenuGroupComponent(
            {"label": label or (self.label if hasattr(self, "_underlying") else None), "components": []}
        )
        group.components = components
        return group

    def _add_component_from_item(self, item: MenuActionItem):
        self.underlying.components.append(item._generate_underlying())

    def _set_components(self, components: list[MenuActionItem]):
        self.underlying.components.clear()
        for component in components:
            self._add_component_from_item(item=component)

    @property
    def view(self) -> V_co | None:
        """Gets the parent view associated with this item.

        The view refers to the structure that holds this item. This is typically set
        automatically when the item is added to a view.

        Returns
        -------
        :class:`BaseView` | :obj:`None`
            The parent view of this item, or ``None`` if the item is not attached to any view.
        """
        if self.parent:
            from .view import BaseView

            if isinstance(self.parent, BaseView):
                return self.parent
            return self.parent.view
        return None

    @property
    def underlying(self) -> OverflowMenuGroupComponent:
        return self._underlying

    @underlying.setter
    def underlying(self, value: OverflowMenuGroupComponent) -> None:
        self._underlying = value

    def is_dispatchable(self) -> bool:
        return any(component.is_dispatchable() for component in self.components)

    def is_persistent(self) -> bool:
        return all(component.is_persistent() for component in self.components)

    def is_storable(self) -> bool:
        return self.is_dispatchable()

    def refresh_component(self, component: OverflowMenuGroupComponent) -> None:
        self.underlying = component
        for i, y in enumerate(component.components):
            x = self.components[i]
            x.refresh_component(y)

    def walk_items(self) -> Iterator[MenuActionItem]:
        yield from self.components

    def to_component_dict(self) -> OverflowMenuGroupComponentPayload:
        self._underlying = self._generate_underlying()
        return self.underlying.to_dict()

    @classmethod
    def from_component(cls, component: OverflowMenuGroupComponent) -> Self:
        components = [MenuActionItem.from_component(c) for c in component.components]
        return cls(
            *components,
            label=component.label,
        )

    callback = None


class MenuActionItem(ViewItem[V_co]):
    """Represents an overflow menu action item.

    .. versionadded:: 2.9

    Parameters
    ----------
    style: :class:`discord.MenuActionItemStyle`
        The style of the item.
    custom_id: :class:`str` | :obj:`None`
        The ID of the item that gets received during an interaction.
        If this item is for a URL, it does not have a custom ID.
    url: :class:`str` | :obj:`None`
        The URL this item sends you to.
    label: :class:`str` | :obj:`None`
        The label of the item, if any.
    emoji: :class:`.PartialEmoji` | :class:`GuildEmoji` | :class:`AppEmoji` | :class:`str` | :obj:`None`
        The emoji of the item, if available.
    id: :class:`int` | :obj:`None`
        The item's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "style",
        "url",
        "label",
        "emoji",
        "custom_id",
        "id",
    )

    def __init__(
        self,
        *,
        style: MenuActionItemStyle = MenuActionItemStyle.default,
        label: str | None = None,
        custom_id: str | None = None,
        url: str | None = None,
        emoji: str | GuildEmoji | AppEmoji | PartialEmoji | None = None,
        id: int | None = None,
    ):
        super().__init__()
        if custom_id is not None and len(str(custom_id)) > 100:
            raise ValueError("custom_id must be 100 characters or fewer")
        if custom_id is not None and url is not None:
            raise TypeError("cannot mix both url and custom_id with Button")

        if not isinstance(custom_id, str) and custom_id is not None:
            raise TypeError(
                f"expected custom_id to be str, not {custom_id.__class__.__name__}"
            )

        self._provided_custom_id = custom_id is not None
        if url is None and custom_id is None:
            custom_id = os.urandom(16).hex()

        if url is not None:
            style = MenuActionItemStyle.link

        if emoji is not None:
            if isinstance(emoji, str):
                emoji = PartialEmoji.from_str(emoji)
            elif isinstance(emoji, _EmojiTag):
                emoji = emoji._to_partial()
            else:
                raise TypeError(
                    "expected emoji to be str, GuildEmoji, AppEmoji, or PartialEmoji not"
                    f" {emoji.__class__}"
                )

        self._underlying = self._generate_underlying(
            custom_id=custom_id,
            url=url,
            label=label,
            style=style,
            emoji=emoji,
            id=id,
        )

    def _generate_underlying(
        self,
        style: MenuActionItemStyle | None = None,
        label: str | None = None,
        custom_id: str | None = None,
        url: str | None = None,
        emoji: str | GuildEmoji | AppEmoji | PartialEmoji | None = None,
        id: int | None = None,
    ) -> MenuActionItemComponent:
        super()._generate_underlying(MenuActionItemComponent)
        return MenuActionItemComponent._raw_construct(
            type=ComponentType.menu_action_item,
            custom_id=custom_id or self.custom_id,
            url=url or self.url,
            label=label or self.label,
            style=style or self.style,
            emoji=emoji or self.emoji,
            id=id or self.id,
        )

    @property
    def style(self) -> MenuActionItemStyle:
        """The style of the item."""
        return self.underlying.style

    @style.setter
    def style(self, value: MenuActionItemStyle):
        self.underlying.style = value

    @property
    def custom_id(self) -> str | None:
        """The ID of the item that gets received during an interaction.

        If this item is for a URL, it does not have a custom ID.
        """
        return self.underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str | None):
        if value is not None and not isinstance(value, str):
            raise TypeError("custom_id must be None or str")
        if value and len(value) > 100:
            raise ValueError("custom_id must be 100 characters or fewer")
        self.underlying.custom_id = value
        self._provided_custom_id = value is not None

    @property
    def url(self) -> str | None:
        """The URL this item sends you to."""
        return self.underlying.url

    @url.setter
    def url(self, value: str | None):
        if value is not None and not isinstance(value, str):
            raise TypeError("url must be None or str")
        self.underlying.url = value

    @property
    def label(self) -> str | None:
        """The label of the item, if available."""
        return self.underlying.label

    @label.setter
    def label(self, value: str | None):
        self.underlying.label = str(value) if value is not None else value

    @property
    def emoji(self) -> PartialEmoji | None:
        """The emoji of the item, if available."""
        return self.underlying.emoji

    @emoji.setter
    def emoji(self, value: str | GuildEmoji | AppEmoji | PartialEmoji | None):  # type: ignore
        if value is None:
            self.underlying.emoji = None
        elif isinstance(value, str):
            self.underlying.emoji = PartialEmoji.from_str(value)
        elif isinstance(value, _EmojiTag):
            self.underlying.emoji = value._to_partial()
        else:
            raise TypeError(
                "expected str, GuildEmoji, AppEmoji, or PartialEmoji, received"
                f" {value.__class__} instead"
            )

    @classmethod
    def from_component(cls, item: MenuActionItemComponent) -> Self:
        return cls(
            style=item.style,
            label=item.label,
            custom_id=item.custom_id,
            url=item.url,
            emoji=item.emoji,
            id=item.id,
        )

    def to_component_dict(self) -> MenuActionItemComponentPayload:
        return super().to_component_dict()

    def is_dispatchable(self) -> bool:
        return (self.custom_id is not None) and (
            bool(self.view._store) if self.view else True
        )

    def is_storable(self) -> bool:
        return self.is_dispatchable()

    def is_persistent(self) -> bool:
        if self.style is MenuActionItemStyle.link:
            return self.url is not None
        return super().is_persistent()

    def refresh_component(self, item: MenuActionItemComponent) -> None:
        self.underlying = item


def action_item(
    *,
    label: str | None = None,
    custom_id: str | None = None,
    style: MenuActionItemStyle = MenuActionItemStyle.default,
    emoji: str | GuildEmoji | AppEmoji | PartialEmoji | None = None,
    id: int | None = None,
) -> Callable[[ItemCallbackType[MenuActionItem[V_co]]], MenuActionItem[V_co]]:
    """A decorator that attaches an item to a overflow menu group.

    The function being decorated should have three parameters, ``self`` representing
    the :class:`discord.ui.View` or :class:`discord.ui.OverflowMenuGroup`, the :class:`discord.ui.MenuActionItem` being pressed, and
    the :class:`discord.Interaction` you receive.

    .. note::

        Link items cannot be created with this decorator. Consider
        creating a :class:`MenuActionItem` object manually instead. These types of
        items do not have a callback associated since Discord doesn't handle
        them when clicked.

    Parameters
    ----------
    label: :class:`str` | :obj:`None`
        The label of the item, if any.
    custom_id: :class:`str` | :obj:`None`
        The ID of the item that gets received during an interaction.
        It is recommended not to set this parameter to prevent conflicts.
    style: :class:`.ButtonStyle`
        The style of the item. Defaults to :attr:`.ButtonStyle.grey`.
    emoji: :class:`str` | :class:`GuildEmoji` | :class:`AppEmoji` | :class:`.PartialEmoji` | :obj:`None`
        The emoji of the item. This can be in string form or a :class:`.PartialEmoji`
        or a full :class:`GuildEmoji` or :class:`AppEmoji`.
    """

    def decorator(func: ItemCallbackType) -> ItemCallbackType:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("item function must be a coroutine function")

        func.__discord_ui_model_type__ = MenuActionItem
        func.__discord_ui_model_kwargs__ = {
            "style": style,
            "custom_id": custom_id,
            "url": None,
            "label": label,
            "emoji": emoji,
            "id": id,
        }
        return func

    return decorator  # type: ignore # lie to the type checkers, because after a View is instated, the button callback is converted into a Button instance
