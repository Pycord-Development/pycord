"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
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
from typing import TYPE_CHECKING, Callable, TypeVar

from ..channel import _threaded_guild_channel_factory
from ..components import SelectMenu, SelectOption
from ..emoji import Emoji
from ..enums import ChannelType, ComponentType
from ..errors import InvalidArgument
from ..interactions import Interaction
from ..member import Member
from ..partial_emoji import PartialEmoji
from ..role import Role
from ..threads import Thread
from ..user import User
from ..utils import MISSING
from .item import Item, ItemCallbackType

__all__ = (
    "Select",
    "select",
    "string_select",
    "user_select",
    "role_select",
    "mentionable_select",
    "channel_select",
)

if TYPE_CHECKING:
    from ..abc import GuildChannel
    from ..types.components import SelectMenu as SelectMenuPayload
    from ..types.interactions import ComponentInteractionData
    from .view import View

S = TypeVar("S", bound="Select")
V = TypeVar("V", bound="View", covariant=True)


class Select(Item[V]):
    """Represents a UI select menu.

    This is usually represented as a drop down menu.

    In order to get the selected items that the user has chosen, use :attr:`Select.values`.

    .. versionadded:: 2.0

    .. versionchanged:: 2.3

        Added support for :attr:`discord.ComponentType.string_select`, :attr:`discord.ComponentType.user_select`,
        :attr:`discord.ComponentType.role_select`, :attr:`discord.ComponentType.mentionable_select`,
        and :attr:`discord.ComponentType.channel_select`.

    Parameters
    ----------
    select_type: :class:`discord.ComponentType`
        The type of select to create. Must be one of
        :attr:`discord.ComponentType.string_select`, :attr:`discord.ComponentType.user_select`,
        :attr:`discord.ComponentType.role_select`, :attr:`discord.ComponentType.mentionable_select`,
        or :attr:`discord.ComponentType.channel_select`.
    custom_id: :class:`str`
        The ID of the select menu that gets received during an interaction.
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
        Whether the select is disabled or not.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    __item_repr_attributes__: tuple[str, ...] = (
        "type",
        "placeholder",
        "min_values",
        "max_values",
        "options",
        "channel_types",
        "disabled",
    )

    def __init__(
        self,
        select_type: ComponentType = ComponentType.string_select,
        *,
        custom_id: str | None = None,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        options: list[SelectOption] = None,
        channel_types: list[ChannelType] = None,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        if options and select_type is not ComponentType.string_select:
            raise InvalidArgument("options parameter is only valid for string selects")
        if channel_types and select_type is not ComponentType.channel_select:
            raise InvalidArgument(
                "channel_types parameter is only valid for channel selects"
            )
        super().__init__()
        self._selected_values: list[str] = []
        self._interaction: Interaction | None = None
        if min_values < 0 or min_values > 25:
            raise ValueError("min_values must be between 0 and 25")
        if max_values < 1 or max_values > 25:
            raise ValueError("max_values must be between 1 and 25")
        if placeholder and len(placeholder) > 150:
            raise ValueError("placeholder must be 150 characters or fewer")
        if not isinstance(custom_id, str) and custom_id is not None:
            raise TypeError(
                f"expected custom_id to be str, not {custom_id.__class__.__name__}"
            )

        self._provided_custom_id = custom_id is not None
        custom_id = os.urandom(16).hex() if custom_id is None else custom_id
        self._underlying: SelectMenu = SelectMenu._raw_construct(
            custom_id=custom_id,
            type=select_type,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
            options=options or [],
            channel_types=channel_types or [],
        )
        self.row = row

    @property
    def custom_id(self) -> str:
        """The ID of the select menu that gets received during an interaction."""
        return self._underlying.custom_id

    @custom_id.setter
    def custom_id(self, value: str):
        if not isinstance(value, str):
            raise TypeError("custom_id must be None or str")
        if len(value) > 100:
            raise ValueError("custom_id must be 100 characters or fewer")
        self._underlying.custom_id = value

    @property
    def placeholder(self) -> str | None:
        """The placeholder text that is shown if nothing is selected, if any."""
        return self._underlying.placeholder

    @placeholder.setter
    def placeholder(self, value: str | None):
        if value is not None and not isinstance(value, str):
            raise TypeError("placeholder must be None or str")
        if value and len(value) > 150:
            raise ValueError("placeholder must be 150 characters or fewer")

        self._underlying.placeholder = value

    @property
    def min_values(self) -> int:
        """The minimum number of items that must be chosen for this select menu."""
        return self._underlying.min_values

    @min_values.setter
    def min_values(self, value: int):
        if value < 0 or value > 25:
            raise ValueError("min_values must be between 0 and 25")
        self._underlying.min_values = int(value)

    @property
    def max_values(self) -> int:
        """The maximum number of items that must be chosen for this select menu."""
        return self._underlying.max_values

    @max_values.setter
    def max_values(self, value: int):
        if value < 1 or value > 25:
            raise ValueError("max_values must be between 1 and 25")
        self._underlying.max_values = int(value)

    @property
    def disabled(self) -> bool:
        """Whether the select is disabled or not."""
        return self._underlying.disabled

    @disabled.setter
    def disabled(self, value: bool):
        self._underlying.disabled = bool(value)

    @property
    def channel_types(self) -> list[ChannelType]:
        """A list of channel types that can be selected in this menu."""
        return self._underlying.channel_types

    @channel_types.setter
    def channel_types(self, value: list[ChannelType]):
        if self._underlying.type is not ComponentType.channel_select:
            raise InvalidArgument("channel_types can only be set on channel selects")
        self._underlying.channel_types = value

    @property
    def options(self) -> list[SelectOption]:
        """A list of options that can be selected in this menu."""
        return self._underlying.options

    @options.setter
    def options(self, value: list[SelectOption]):
        if self._underlying.type is not ComponentType.string_select:
            raise InvalidArgument("options can only be set on string selects")
        if not isinstance(value, list):
            raise TypeError("options must be a list of SelectOption")
        if not all(isinstance(obj, SelectOption) for obj in value):
            raise TypeError("all list items must subclass SelectOption")

        self._underlying.options = value

    def add_option(
        self,
        *,
        label: str,
        value: str = MISSING,
        description: str | None = None,
        emoji: str | Emoji | PartialEmoji | None = None,
        default: bool = False,
    ):
        """Adds an option to the select menu.

        To append a pre-existing :class:`discord.SelectOption` use the
        :meth:`append_option` method instead.

        Parameters
        ----------
        label: :class:`str`
            The label of the option. This is displayed to users.
            Can only be up to 100 characters.
        value: :class:`str`
            The value of the option. This is not displayed to users.
            If not given, defaults to the label. Can only be up to 100 characters.
        description: Optional[:class:`str`]
            An additional description of the option, if any.
            Can only be up to 100 characters.
        emoji: Optional[Union[:class:`str`, :class:`.Emoji`, :class:`.PartialEmoji`]]
            The emoji of the option, if available. This can either be a string representing
            the custom or unicode emoji or an instance of :class:`.PartialEmoji` or :class:`.Emoji`.
        default: :class:`bool`
            Whether this option is selected by default.

        Raises
        ------
        ValueError
            The number of options exceeds 25.
        """
        if self._underlying.type is not ComponentType.string_select:
            raise Exception("options can only be set on string selects")

        option = SelectOption(
            label=label,
            value=value,
            description=description,
            emoji=emoji,
            default=default,
        )

        self.append_option(option)

    def append_option(self, option: SelectOption):
        """Appends an option to the select menu.

        Parameters
        ----------
        option: :class:`discord.SelectOption`
            The option to append to the select menu.

        Raises
        ------
        ValueError
            The number of options exceeds 25.
        """
        if self._underlying.type is not ComponentType.string_select:
            raise Exception("options can only be set on string selects")

        if len(self._underlying.options) > 25:
            raise ValueError("maximum number of options already provided")

        self._underlying.options.append(option)

    @property
    def values(
        self,
    ) -> list[str] | list[Member | User] | list[Role] | list[
        Member | User | Role
    ] | list[GuildChannel | Thread]:
        """Union[List[:class:`str`], List[Union[:class:`discord.Member`, :class:`discord.User`]], List[:class:`discord.Role`]],
        List[Union[:class:`discord.Member`, :class:`discord.User`, :class:`discord.Role`]], List[:class:`discord.abc.GuildChannel`]]:
        A list of values that have been selected by the user.
        """
        select_type = self._underlying.type
        if select_type is ComponentType.string_select:
            return self._selected_values
        resolved = []
        selected_values = list(self._selected_values)
        state = self._interaction._state
        guild = self._interaction.guild
        resolved_data = self._interaction.data.get("resolved", {})
        if select_type is ComponentType.channel_select:
            for channel_id, _data in resolved_data.get("channels", {}).items():
                if channel_id not in selected_values:
                    continue
                if (
                    int(channel_id) in guild._channels
                    or int(channel_id) in guild._threads
                ):
                    result = guild.get_channel_or_thread(int(channel_id))
                    _data["_invoke_flag"] = True
                    result._update(_data) if isinstance(
                        result, Thread
                    ) else result._update(guild, _data)
                else:
                    # NOTE:
                    # This is a fallback in case the channel/thread is not found in the
                    # guild's channels/threads. For channels, if this fallback occurs, at the very minimum,
                    # permissions will be incorrect due to a lack of permission_overwrite data.
                    # For threads, if this fallback occurs, info like thread owner id, message count,
                    # flags, and more will be missing due to a lack of data sent by Discord.
                    obj_type = _threaded_guild_channel_factory(_data["type"])[0]
                    result = obj_type(state=state, data=_data, guild=guild)
                resolved.append(result)
        elif select_type in (
            ComponentType.user_select,
            ComponentType.mentionable_select,
        ):
            cache_flag = state.member_cache_flags.interaction
            resolved_user_data = resolved_data.get("users", {})
            resolved_member_data = resolved_data.get("members", {})
            for _id in selected_values:
                if (_data := resolved_user_data.get(_id)) is not None:
                    if (_member_data := resolved_member_data.get(_id)) is not None:
                        member = dict(_member_data)
                        member["user"] = _data
                        _data = member
                        result = guild._get_and_update_member(
                            _data, int(_id), cache_flag
                        )
                    else:
                        result = User(state=state, data=_data)
                    resolved.append(result)
        if select_type in (ComponentType.role_select, ComponentType.mentionable_select):
            for role_id, _data in resolved_data.get("roles", {}).items():
                if role_id not in selected_values:
                    continue
                resolved.append(Role(guild=guild, state=state, data=_data))
        return resolved

    @property
    def width(self) -> int:
        return 5

    def to_component_dict(self) -> SelectMenuPayload:
        return self._underlying.to_dict()

    def refresh_component(self, component: SelectMenu) -> None:
        self._underlying = component

    def refresh_state(self, interaction: Interaction) -> None:
        data: ComponentInteractionData = interaction.data  # type: ignore
        self._selected_values = data.get("values", [])
        self._interaction = interaction

    @classmethod
    def from_component(cls: type[S], component: SelectMenu) -> S:
        return cls(
            select_type=component.type,
            custom_id=component.custom_id,
            placeholder=component.placeholder,
            min_values=component.min_values,
            max_values=component.max_values,
            options=component.options,
            channel_types=component.channel_types,
            disabled=component.disabled,
            row=None,
        )

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def is_dispatchable(self) -> bool:
        return True


_select_types = (
    ComponentType.string_select,
    ComponentType.user_select,
    ComponentType.role_select,
    ComponentType.mentionable_select,
    ComponentType.channel_select,
)


def select(
    select_type: ComponentType = ComponentType.string_select,
    *,
    placeholder: str | None = None,
    custom_id: str | None = None,
    min_values: int = 1,
    max_values: int = 1,
    options: list[SelectOption] = MISSING,
    channel_types: list[ChannelType] = MISSING,
    disabled: bool = False,
    row: int | None = None,
) -> Callable[[ItemCallbackType], ItemCallbackType]:
    """A decorator that attaches a select menu to a component.

    The function being decorated should have three parameters, ``self`` representing
    the :class:`discord.ui.View`, the :class:`discord.ui.Select` being pressed and
    the :class:`discord.Interaction` you receive.

    In order to get the selected items that the user has chosen within the callback
    use :attr:`Select.values`.

    .. versionchanged:: 2.3

        Creating select menus of different types is now supported.

    Parameters
    ----------
    select_type: :class:`discord.ComponentType`
        The type of select to create. Must be one of
        :attr:`discord.ComponentType.string_select`, :attr:`discord.ComponentType.user_select`,
        :attr:`discord.ComponentType.role_select`, :attr:`discord.ComponentType.mentionable_select`,
        or :attr:`discord.ComponentType.channel_select`.
    placeholder: Optional[:class:`str`]
        The placeholder text that is shown if nothing is selected, if any.
    custom_id: :class:`str`
        The ID of the select menu that gets received during an interaction.
        It is recommended not to set this parameter to prevent conflicts.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    min_values: :class:`int`
        The minimum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 0 and 25.
    max_values: :class:`int`
        The maximum number of items that must be chosen for this select menu.
        Defaults to 1 and must be between 1 and 25.
    options: List[:class:`discord.SelectOption`]
        A list of options that can be selected in this menu.
        Only valid for the :attr:`discord.ComponentType.string_select` type.
    channel_types: List[:class:`discord.ChannelType`]
        The channel types that should be selectable.
        Only valid for the :attr:`discord.ComponentType.channel_select` type.
        Defaults to all channel types.
    disabled: :class:`bool`
        Whether the select is disabled or not. Defaults to ``False``.
    """
    if select_type not in _select_types:
        raise ValueError(
            "select_type must be one of " + ", ".join([i.name for i in _select_types])
        )

    if options is not MISSING and select_type not in (
        ComponentType.select,
        ComponentType.string_select,
    ):
        raise TypeError("options may only be specified for string selects")

    if channel_types is not MISSING and select_type is not ComponentType.channel_select:
        raise TypeError("channel_types may only be specified for channel selects")

    def decorator(func: ItemCallbackType) -> ItemCallbackType:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("select function must be a coroutine function")

        model_kwargs = {
            "select_type": select_type,
            "placeholder": placeholder,
            "custom_id": custom_id,
            "row": row,
            "min_values": min_values,
            "max_values": max_values,
            "disabled": disabled,
        }
        if options:
            model_kwargs["options"] = options
        if channel_types:
            model_kwargs["channel_types"] = channel_types

        func.__discord_ui_model_type__ = Select
        func.__discord_ui_model_kwargs__ = model_kwargs

        return func

    return decorator


def string_select(
    *,
    placeholder: str | None = None,
    custom_id: str | None = None,
    min_values: int = 1,
    max_values: int = 1,
    options: list[SelectOption] = MISSING,
    disabled: bool = False,
    row: int | None = None,
) -> Callable[[ItemCallbackType], ItemCallbackType]:
    """A shortcut for :meth:`discord.ui.select` with select type :attr:`discord.ComponentType.string_select`.

    .. versionadded:: 2.3
    """
    return select(
        ComponentType.string_select,
        placeholder=placeholder,
        custom_id=custom_id,
        min_values=min_values,
        max_values=max_values,
        options=options,
        disabled=disabled,
        row=row,
    )


def user_select(
    *,
    placeholder: str | None = None,
    custom_id: str | None = None,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    row: int | None = None,
) -> Callable[[ItemCallbackType], ItemCallbackType]:
    """A shortcut for :meth:`discord.ui.select` with select type :attr:`discord.ComponentType.user_select`.

    .. versionadded:: 2.3
    """
    return select(
        ComponentType.user_select,
        placeholder=placeholder,
        custom_id=custom_id,
        min_values=min_values,
        max_values=max_values,
        disabled=disabled,
        row=row,
    )


def role_select(
    *,
    placeholder: str | None = None,
    custom_id: str | None = None,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    row: int | None = None,
) -> Callable[[ItemCallbackType], ItemCallbackType]:
    """A shortcut for :meth:`discord.ui.select` with select type :attr:`discord.ComponentType.role_select`.

    .. versionadded:: 2.3
    """
    return select(
        ComponentType.role_select,
        placeholder=placeholder,
        custom_id=custom_id,
        min_values=min_values,
        max_values=max_values,
        disabled=disabled,
        row=row,
    )


def mentionable_select(
    *,
    placeholder: str | None = None,
    custom_id: str | None = None,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    row: int | None = None,
) -> Callable[[ItemCallbackType], ItemCallbackType]:
    """A shortcut for :meth:`discord.ui.select` with select type :attr:`discord.ComponentType.mentionable_select`.

    .. versionadded:: 2.3
    """
    return select(
        ComponentType.mentionable_select,
        placeholder=placeholder,
        custom_id=custom_id,
        min_values=min_values,
        max_values=max_values,
        disabled=disabled,
        row=row,
    )


def channel_select(
    *,
    placeholder: str | None = None,
    custom_id: str | None = None,
    min_values: int = 1,
    max_values: int = 1,
    disabled: bool = False,
    channel_types: list[ChannelType] = MISSING,
    row: int | None = None,
) -> Callable[[ItemCallbackType], ItemCallbackType]:
    """A shortcut for :meth:`discord.ui.select` with select type :attr:`discord.ComponentType.channel_select`.

    .. versionadded:: 2.3
    """
    return select(
        ComponentType.channel_select,
        placeholder=placeholder,
        custom_id=custom_id,
        min_values=min_values,
        max_values=max_values,
        disabled=disabled,
        channel_types=channel_types,
        row=row,
    )
