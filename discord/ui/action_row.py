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

from collections.abc import Sequence
from functools import partial
from typing import TYPE_CHECKING, ClassVar, Iterator, Literal, TypeVar, overload

from ..components import ActionRow as ActionRowComponent
from ..components import SelectDefaultValue, SelectOption, _component_factory
from ..enums import ButtonStyle, ChannelType, ComponentType
from ..utils import find, get
from .button import Button
from .file import File
from .item import ItemCallbackType, ViewItem
from .select import Select

__all__ = ("ActionRow",)

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..emoji import AppEmoji, GuildEmoji
    from ..partial_emoji import PartialEmoji, _EmojiTag
    from ..types.components import ActionRow as ActionRowPayload
    from .view import DesignerView


A = TypeVar("A", bound="ActionRow")
V = TypeVar("V", bound="DesignerView", covariant=True)


class ActionRow(ViewItem[V]):
    """Represents a UI Action Row used in :class:`discord.ui.DesignerView`.

    The items supported are as follows:

    - :class:`discord.ui.Select`
    - :class:`discord.ui.Button`

    .. versionadded:: 2.7

    Parameters
    ----------
    *items: :class:`ViewItem`
        The initial items in this action row.
    id: Optional[:class:`int`]
        The action's ID.
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "items",
        "id",
    )

    __row_children_items__: ClassVar[list[ItemCallbackType]] = []

    def __init_subclass__(cls) -> None:
        children: list[ItemCallbackType] = []
        for base in reversed(cls.__mro__):
            for member in base.__dict__.values():
                if hasattr(member, "__discord_ui_model_type__"):
                    children.append(member)

        cls.__row_children_items__ = children

    def __init__(
        self,
        *items: ViewItem,
        id: int | None = None,
    ):
        super().__init__()

        self.children: list[ViewItem] = []

        self._underlying = ActionRowComponent._raw_construct(
            type=ComponentType.action_row,
            id=id,
            children=[],
        )

        for func in self.__row_children_items__:
            item: ViewItem = func.__discord_ui_model_type__(
                **func.__discord_ui_model_kwargs__
            )
            item.callback = partial(func, self, item)
            self.add_item(item)
            setattr(self, func.__name__, item)
        for i in items:
            self.add_item(i)

    def _add_component_from_item(self, item: ViewItem):
        self._underlying.children.append(item._underlying)

    def _set_components(self, items: list[ViewItem]):
        self._underlying.children.clear()
        for item in items:
            self._add_component_from_item(item)

    def add_item(self, item: ViewItem) -> Self:
        """Adds an item to the action row.

        Parameters
        ----------
        item: :class:`ViewItem`
            The item to add to the action row.

        Raises
        ------
        TypeError
            A :class:`ViewItem` was not passed.
        """

        if not isinstance(item, (Select, Button)):
            raise TypeError(f"expected Select or Button, not {item.__class__!r}")
        if item.row:
            raise ValueError(f"{item.__class__!r}.row is not supported in ActionRow")
        if self.width + item.width > 5:
            raise ValueError(f"Not enough space left on this ActionRow")

        item._view = self.view
        item.parent = self

        self.children.append(item)
        self._add_component_from_item(item)
        return self

    def remove_item(self, item: ViewItem | str | int) -> Self:
        """Removes an item from the action row. If an int or str is passed, it will remove by Item :attr:`id` or ``custom_id`` respectively.

        Parameters
        ----------
        item: Union[:class:`ViewItem`, :class:`int`, :class:`str`]
            The item, ``id``, or item ``custom_id`` to remove from the action row.
        """

        if isinstance(item, (str, int)):
            item = self.get_item(item)
        try:
            self.children.remove(item)
        except ValueError:
            pass
        return self

    def get_item(self, id: str | int) -> ViewItem | None:
        """Get an item from this action row. Roughly equivalent to `utils.get(row.children, ...)`.
        If an ``int`` is provided, the item will be retrieved by ``id``, otherwise by ``custom_id``.

        Parameters
        ----------
        id: Union[:class:`str`, :class:`int`]
            The id or custom_id of the item to get.

        Returns
        -------
        Optional[:class:`ViewItem`]
            The item with the matching ``id`` or ``custom_id`` if it exists.
        """
        if not id:
            return None
        attr = "id" if isinstance(id, int) else "custom_id"
        child = find(lambda i: getattr(i, attr, None) == id, self.children)
        return child

    def add_button(
        self,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: str | None = None,
        disabled: bool = False,
        custom_id: str | None = None,
        url: str | None = None,
        emoji: str | GuildEmoji | AppEmoji | PartialEmoji | None = None,
        sku_id: int | None = None,
        id: int | None = None,
    ) -> Self:
        """Adds a :class:`Button` to the action row.

        To append a pre-existing :class:`Button`, use the
        :meth:`add_item` method instead.

        Parameters
        ----------
        style: :class:`discord.ButtonStyle`
            The style of the button.
        custom_id: Optional[:class:`str`]
            The custom ID of the button that gets received during an interaction.
            If this button is for a URL, it does not have a custom ID.
        url: Optional[:class:`str`]
            The URL this button sends you to.
        disabled: :class:`bool`
            Whether the button is disabled or not.
        label: Optional[:class:`str`]
            The label of the button, if any. Maximum of 80 chars.
        emoji: Optional[Union[:class:`.PartialEmoji`, :class:`GuildEmoji`, :class:`AppEmoji`, :class:`str`]]
            The emoji of the button, if any.
        sku_id: Optional[Union[:class:`int`]]
            The ID of the SKU this button refers to.
        id: Optional[:class:`int`]
            The button's ID.
        """

        button = Button(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            sku_id=sku_id,
            id=id,
        )

        return self.add_item(button)

    @overload
    def add_select(
        self,
        select_type: Literal[ComponentType.string_select] = ...,
        *,
        custom_id: str | None = ...,
        placeholder: str | None = ...,
        min_values: int = ...,
        max_values: int = ...,
        options: list[SelectOption] | None = ...,
        disabled: bool = ...,
        id: int | None = ...,
    ) -> None: ...

    @overload
    def add_select(
        self,
        select_type: Literal[ComponentType.channel_select] = ...,
        *,
        custom_id: str | None = ...,
        placeholder: str | None = ...,
        min_values: int = ...,
        max_values: int = ...,
        channel_types: list[ChannelType] | None = ...,
        disabled: bool = ...,
        id: int | None = ...,
        default_values: Sequence[SelectDefaultValue] | None = ...,
    ) -> None: ...

    @overload
    def add_select(
        self,
        select_type: Literal[
            ComponentType.user_select,
            ComponentType.role_select,
            ComponentType.mentionable_select,
        ] = ...,
        *,
        custom_id: str | None = ...,
        placeholder: str | None = ...,
        min_values: int = ...,
        max_values: int = ...,
        disabled: bool = ...,
        id: int | None = ...,
        default_values: Sequence[SelectDefaultValue] | None = ...,
    ) -> None: ...

    def add_select(
        self,
        select_type: ComponentType = ComponentType.string_select,
        *,
        custom_id: str | None = None,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        options: list[SelectOption] | None = None,
        channel_types: list[ChannelType] | None = None,
        disabled: bool = False,
        id: int | None = None,
        default_values: Sequence[SelectDefaultValue] | None = None,
    ) -> Self:
        """Adds a :class:`Select` to the container.

        To append a pre-existing :class:`Select`, use the
        :meth:`add_item` method instead.

        Parameters
        ----------
        select_type: :class:`discord.ComponentType`
            The type of select to create. Must be one of
            :attr:`discord.ComponentType.string_select`, :attr:`discord.ComponentType.user_select`,
            :attr:`discord.ComponentType.role_select`, :attr:`discord.ComponentType.mentionable_select`,
            or :attr:`discord.ComponentType.channel_select`.
        custom_id: :class:`str`
            The custom ID of the select menu that gets received during an interaction.
            If not given then one is generated for you.
        placeholder: Optional[:class:`str`]
            The placeholder text that is shown if nothing is selected, if any.
        min_values: :class:`int`
            The minimum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        max_values: :class:`int`
            The maximum number of items that must be chosen for this select menu.
            Defaults to 1 and must be between 1 and 25.
        options: List[:class:`discord.SelectOption`]
            A list of options that can be selected in this menu.
            Only valid for selects of type :attr:`discord.ComponentType.string_select`.
        channel_types: List[:class:`discord.ChannelType`]
            A list of channel types that can be selected in this menu.
            Only valid for selects of type :attr:`discord.ComponentType.channel_select`.
        disabled: :class:`bool`
            Whether the select is disabled or not. Defaults to ``False``.
        id: Optional[:class:`int`]
            The select menu's ID.
        default_values: Optional[Sequence[Union[:class:`discord.SelectDefaultValue`, :class:`discord.abc.Snowflake`]]]
            The default values of this select. Only applicable if :attr:`.select_type` is not :attr:`discord.ComponentType.string_select`.

            These can be either :class:`discord.SelectDefaultValue` instances or models, which will be converted into :class:`discord.SelectDefaultValue`
            instances.
        """

        select = Select(
            select_type=select_type,
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options or [],
            channel_types=channel_types or [],
            disabled=disabled,
            id=id,
            default_values=default_values,
        )

        return self.add_item(select)

    @ViewItem.view.setter
    def view(self, value):
        self._view = value
        for item in self.children:
            item.parent = self
            item._view = value

    def is_dispatchable(self) -> bool:
        return any(item.is_dispatchable() for item in self.children)

    def is_persistent(self) -> bool:
        return all(item.is_persistent() for item in self.children)

    def refresh_component(self, component: ActionRowComponent) -> None:
        self._underlying = component
        i = 0
        for y in component.components:
            x = self.children[i]
            x.refresh_component(y)
            i += 1

    def disable_all_items(self, *, exclusions: list[ViewItem] | None = None) -> Self:
        """
        Disables all items in the row.

        Parameters
        ----------
        exclusions: Optional[List[:class:`ViewItem`]]
            A list of items in `self.children` to not disable.
        """
        for item in self.walk_items():
            if exclusions is None or item not in exclusions:
                item.disabled = True
        return self

    def enable_all_items(self, *, exclusions: list[ViewItem] | None = None) -> Self:
        """
        Enables all items in the row.

        Parameters
        ----------
        exclusions: Optional[List[:class:`ViewItem`]]
            A list of items in `self.children` to not enable.
        """
        for item in self.walk_items():
            if exclusions is None or item not in exclusions:
                item.disabled = False
        return self

    @property
    def width(self):
        """Return the sum of the items' widths."""
        t = 0
        for item in self.children:
            t += 1 if item._underlying.type is ComponentType.button else 5
        return t

    def walk_items(self) -> Iterator[ViewItem]:
        yield from self.children

    def to_component_dict(self) -> ActionRowPayload:
        self._set_components(self.items)
        return super().to_component_dict()

    @classmethod
    def from_component(cls: type[A], component: ActionRowComponent) -> A:
        from .view import _component_to_item, _walk_all_components

        items = [
            _component_to_item(c) for c in _walk_all_components(component.components)
        ]
        return cls(
            *items,
            id=component.id,
        )

    callback = None
