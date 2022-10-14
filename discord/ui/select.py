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

from ..member import Member
from ..role import Role
from ..threads import Thread
from ..user import User
from ..channel import _threaded_guild_channel_factory
from ..components import (
    ChannelSelectMenu,
    MentionableSelectMenu,
    RoleSelectMenu,
    SelectMenu,
    SelectOption,
    UserSelectMenu,
)
from ..emoji import Emoji
from ..enums import ChannelType, ComponentType
from ..interactions import Interaction
from ..partial_emoji import PartialEmoji
from ..utils import MISSING
from .item import Item, ItemCallbackType

__all__ = (
    "Select",
    "UserSelect",
    "RoleSelect",
    "MentionableSelect",
    "ChannelSelect",
    "select",
    "user_select",
    "role_select",
    "mentionable_select",
    "channel_select",
)

if TYPE_CHECKING:
    from ..components import _BaseSelectMenu
    from ..types.components import SelectMenu as SelectMenuPayload
    from ..types.interactions import ComponentInteractionData
    from .view import View

S = TypeVar("S", bound="Select")
V = TypeVar("V", bound="View", covariant=True)

_select_component_types = {
    3: SelectMenu,
    5: UserSelectMenu,
    6: RoleSelectMenu,
    7: MentionableSelectMenu,
    8: ChannelSelectMenu,
}


class _BaseSelect(Item[V]):
    __item_repr_attributes__: tuple[str, ...] = (
        "placeholder",
        "min_values",
        "max_values",
        "options",
        "disabled",
    )

    def __init__(
        self,
        select_type: int,
        *,
        custom_id: str | None = None,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        super().__init__()
        self._selected_values: list[str] = []
        self._interaction: Interaction = None  # type: ignore
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
        self._underlying: _BaseSelectMenu = _select_component_types[
            select_type.value
        ]._raw_construct(
            custom_id=custom_id,
            type=select_type,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
        )
        self.row = row

    @property
    def custom_id(self) -> str:
        """:class:`str`: The ID of the select menu that gets received during an interaction."""
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
        """Optional[:class:`str`]: The placeholder text that is shown if nothing is selected, if any."""
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
        """:class:`int`: The minimum number of items that must be chosen for this select menu."""
        return self._underlying.min_values

    @min_values.setter
    def min_values(self, value: int):
        if value < 0 or value > 25:
            raise ValueError("min_values must be between 0 and 25")
        self._underlying.min_values = int(value)

    @property
    def max_values(self) -> int:
        """:class:`int`: The maximum number of items that must be chosen for this select menu."""
        return self._underlying.max_values

    @max_values.setter
    def max_values(self, value: int):
        if value < 1 or value > 25:
            raise ValueError("max_values must be between 1 and 25")
        self._underlying.max_values = int(value)

    @property
    def disabled(self) -> bool:
        """:class:`bool`: Whether the select is disabled or not."""
        return self._underlying.disabled

    @disabled.setter
    def disabled(self, value: bool):
        self._underlying.disabled = bool(value)

    @property
    def values(self) -> list[str]:
        """List[:class:`str`]: A list of values that have been selected by the user."""
        return self._selected_values

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
            custom_id=component.custom_id,
            placeholder=component.placeholder,
            min_values=component.min_values,
            max_values=component.max_values,
            options=component.options,
            disabled=component.disabled,
            row=None,
        )

    @property
    def type(self) -> ComponentType:
        return self._underlying.type

    def is_dispatchable(self) -> bool:
        return True


class Select(_BaseSelect):
    """Represents a UI select menu.

    This is usually represented as a drop down menu.

    In order to get the selected items that the user has chosen, use :attr:`Select.values`.

    .. versionadded:: 2.0

    Parameters
    ----------
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
    disabled: :class:`bool`
        Whether the select is disabled or not.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    _underlying: SelectMenu
    __item_repr_attributes__: tuple[str, ...] = (
        "placeholder",
        "min_values",
        "max_values",
        "options",
        "disabled",
    )

    def __init__(self, *, options: list[SelectOption] = MISSING, **kwargs) -> None:
        super().__init__(ComponentType.string_select, **kwargs)
        self._underlying.options = [] if options is MISSING else options

    @property
    def options(self) -> list[SelectOption]:
        """List[:class:`discord.SelectOption`]: A list of options that can be selected in this menu."""
        return self._underlying.options

    @options.setter
    def options(self, value: list[SelectOption]):
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

        if len(self._underlying.options) > 25:
            raise ValueError("maximum number of options already provided")

        self._underlying.options.append(option)


class UserSelect(_BaseSelect):
    """Represents a UI select menu.

    This is almost identical to a :class:`discord.ui.Select`,
    except it allows you to select users and does not take
    preset options.

    In order to get the selected items that the user has chosen, use :attr:`Select.values`.

    .. versionadded:: 2.3

    Parameters
    ----------
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
    disabled: :class:`bool`
        Whether the select is disabled or not.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    _underlying: UserSelectMenu

    def __init__(self, **kwargs) -> None:
        super().__init__(ComponentType.user_select, **kwargs)

    @property
    def values(self) -> list[User, Member]:
        """List[:class:`discord.User`, :class:`discord.Member`]:
        A list of users that have been selected by the user.
        """
        resolved = []
        selected_values = self._selected_values
        state = self._interaction._state
        cache_flag = state.member_cache_flags.interaction
        guild = self._interaction.guild
        resolved_data = self._interaction.data.get("resolved", {})
        resolved_member_data = resolved_data.get("members", {})
        for user_id, _data in resolved_data.get("users", {}).items():
            if user_id not in selected_values:
                continue
            if (_member_data := resolved_member_data.get(user_id)) is not None:
                member = dict(_member_data)
                member["user"] = _data
                _data = member
                result = guild._get_and_update_member(_data, int(user_id), cache_flag)
            else:
                result = User(state=state, data=_data)
            resolved.append(result)
        return resolved


class RoleSelect(_BaseSelect):
    """Represents a UI select menu.

    This is almost identical to a :class:`discord.ui.Select`,
    except it allows you to select roles and does not take
    preset options.

    In order to get the selected items that the user has chosen, use :attr:`Select.values`.

    .. versionadded:: 2.3

    Parameters
    ----------
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
    disabled: :class:`bool`
        Whether the select is disabled or not.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    _underlying: RoleSelectMenu

    def __init__(self, **kwargs) -> None:
        super().__init__(ComponentType.role_select, **kwargs)

    @property
    def values(self) -> list[Role]:
        """List[:class:`discord.Role`]:
        A list of roles that have been selected by the user.
        """
        resolved = []
        selected_values = self._selected_values
        state = self._interaction._state
        guild = self._interaction.guild
        resolved_data = self._interaction.data.get("resolved", {})
        for role_id, _data in resolved_data.get("roles", {}).items():
            if role_id not in selected_values:
                continue
            resolved.append(Role(guild=guild, state=state, data=_data))
        return resolved


class MentionableSelect(_BaseSelect):
    """Represents a UI select menu.

    This is almost identical to a :class:`discord.ui.Select`,
    except it allows you to select mentionables (roles/users)
    and does not take preset options.

    In order to get the selected items that the user has chosen, use :attr:`Select.values`.

    .. versionadded:: 2.3

    Parameters
    ----------
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
    disabled: :class:`bool`
        Whether the select is disabled or not.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    _underlying: MentionableSelectMenu

    def __init__(self, **kwargs) -> None:
        super().__init__(ComponentType.mentionable_select, **kwargs)

    @property
    def values(self) -> list[User, Member]:
        """List[:class:`discord.User`, :class:`discord.Member`, :class:`discord.Role`]:
        A list of mentionables that have been selected by the user.
        """
        resolved = []
        selected_values = self._selected_values
        state = self._interaction._state
        cache_flag = state.member_cache_flags.interaction
        guild = self._interaction.guild
        resolved_data = self._interaction.data.get("resolved", {})
        resolved_user_data = resolved_data.get("users", {})
        resolved_member_data = resolved_data.get("members", {})
        resolved_role_data = resolved_data.get("roles", {})
        for _id in selected_values:
            if (_data := resolved_user_data.get(_id)) is not None:
                if (_member_data := resolved_member_data.get(_id)) is not None:
                    member = dict(_member_data)
                    member["user"] = _data
                    _data = member
                    result = guild._get_and_update_member(_data, int(_id), cache_flag)
                else:
                    result = User(state=state, data=_data)
                resolved.append(result)
            elif (_data := resolved_role_data.get(_id)) is not None:
                resolved.append(Role(guild=guild, state=state, data=_data))
        return resolved


class ChannelSelect(_BaseSelect):
    """Represents a UI select menu.

    This is almost identical to a :class:`discord.ui.Select`,
    except it allows you to select channels
    and does not take preset options.

    In order to get the selected items that the user has chosen, use :attr:`Select.values`.

    .. versionadded:: 2.3

    Parameters
    ----------
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
    disabled: :class:`bool`
        Whether the select is disabled or not.
    channel_types: List[:class:`discord.ChannelType`]
        The channel types that should be selectable.
        Defaults to all channel types.
    row: Optional[:class:`int`]
        The relative row this select menu belongs to. A Discord component can only have 5
        rows. By default, items are arranged automatically into those 5 rows. If you'd
        like to control the relative positioning of the row then passing an index is advised.
        For example, row=1 will show up before row=2. Defaults to ``None``, which is automatic
        ordering. The row number must be between 0 and 4 (i.e. zero indexed).
    """

    _underlying: ChannelSelectMenu

    def __init__(self, *, channel_types: ChannelType = MISSING, **kwargs) -> None:
        super().__init__(ComponentType.channel_select, **kwargs)
        self._underlying.channel_types = (
            [] if channel_types is MISSING else channel_types
        )

    @property
    def values(self) -> list[Role]:
        """List[:class:`discord.abc.GuildChannel`, :class:`discord.Thread`]:
        A list of channels that have been selected by the user.
        """
        resolved = []
        selected_values = self._selected_values
        state = self._interaction._state
        guild = self._interaction.guild
        resolved_data = self._interaction.data.get("resolved", {})
        for channel_id, _data in resolved_data.get("channels", {}).items():
            if channel_id not in selected_values:
                continue
            if int(channel_id) in guild._channels or int(channel_id) in guild._threads:
                result = guild.get_channel_or_thread(int(channel_id))
                _data["_invoke_flag"] = True
                result._update(_data) if isinstance(result, Thread) else result._update(
                    guild, _data
                )
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
        return resolved

    @property
    def channel_types(self):
        """List[:class:`discord.ChannelType`]: A list of channel types that can be selected in this menu."""
        return self._underlying.channel_types

    @channel_types.setter
    def channel_types(self, value: list[ChannelType]):
        if not isinstance(value, list):
            raise TypeError("channel types must be a list of ChannelType")
        if not all(isinstance(obj, ChannelType) for obj in value):
            raise TypeError("all list items must be a ChannelType")

        self._underlying.channel_types = value


_select_classes = {
    ComponentType.select: Select,
    ComponentType.string_select: Select,
    ComponentType.user_select: UserSelect,
    ComponentType.role_select: RoleSelect,
    ComponentType.mentionable_select: MentionableSelect,
    ComponentType.channel_select: ChannelSelect,
}


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

        Creating other select menus is now supported.

    Parameters
    ----------
    select_type: :class:`ComponentType`
        The type of select to create. Must be
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
        Only valid for the :attr:`ComponentType.string_select` type.
    channel_types: List[:class:`discord.ChannelType`]
        The channel types that should be selectable.
        Only valid for the :attr:`ComponentType.channel_select` type.
        Defaults to all channel types.
    disabled: :class:`bool`
        Whether the select is disabled or not. Defaults to ``False``.
    """
    if select_type not in _select_classes:
        raise ValueError(
            "select_type must be one of "
            + ", ".join([i.name for i in _select_classes.keys()])
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

        func.__discord_ui_model_type__ = _select_classes[select_type]
        model_kwargs = {
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
