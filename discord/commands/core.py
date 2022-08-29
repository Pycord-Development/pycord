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

import asyncio
import inspect
import re
import types
from collections import OrderedDict
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from ..channel import _threaded_guild_channel_factory
from ..enums import MessageType, SlashCommandOptionType, try_enum, Enum as DiscordEnum
from ..errors import ClientException, ValidationError
from ..member import Member
from ..message import Attachment, Message
from ..object import Object
from ..role import Role
from ..threads import Thread
from ..user import User
from ..utils import find, MISSING
from .mixins import Invokable, _BaseCommand, CogT
from .context import ApplicationContext, AutocompleteContext
from .options import Option, OptionChoice

__all__ = (
    "_BaseCommand",
    "ApplicationCommand",
    "SlashCommand",
    "slash_command",
    "application_command",
    "user_command",
    "message_command",
    "command",
    "SlashCommandGroup",
    "ContextMenuCommand",
    "UserCommand",
    "MessageCommand",
)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from .. import Permissions
    from .mixins import BaseContext

    P = ParamSpec("P")
else:
    P = TypeVar("P")


T = TypeVar("T")


def _validate_names(obj):
    validate_chat_input_name(obj.name)
    if obj.name_localizations:
        for locale, string in obj.name_localizations.items():
            validate_chat_input_name(string, locale=locale)


def _validate_descriptions(obj):
    validate_chat_input_description(obj.description)
    if obj.description_localizations:
        for locale, string in obj.description_localizations.items():
            validate_chat_input_description(string, locale=locale)


class ApplicationCommand(Invokable, _BaseCommand, Generic[CogT, P, T]):
    """Base class for all Application Commands, including:

      - :class:`SlashCommand`
      - :class:`SlashCommandGroup`
      - :class:`ContextMenuCommand` which in turn is a superclass of
      - :class:`MessageCommand` and
      - :class:`UserCommand`
    
    This is a subclass of :class:`.Invokable`.
    """
    __original_kwargs__: Dict[str, Any]
    cog = None

    def __init__(self, func: Callable, **kwargs) -> None:
        super().__init__(func, **kwargs)
        self.id: Optional[int] = kwargs.get("id")
        self.guild_ids: Optional[List[int]] = kwargs.get("guild_ids", None)

        # Permissions
        self.default_member_permissions: Optional["Permissions"] = getattr(
            func, "__default_member_permissions__", kwargs.get("default_member_permissions", None)
        )
        self.guild_only: Optional[bool] = getattr(func, "__guild_only__", kwargs.get("guild_only", None))

    def __repr__(self) -> str:
        return f"<discord.commands.{self.__class__.__name__} name={self.name}>"

    def __eq__(self, other) -> bool:
        if getattr(self, "id", None) is not None and getattr(other, "id", None) is not None:
            check = self.id == other.id
        else:
            check = self.name == other.name and self.guild_ids == other.guild_ids
        return isinstance(other, self.__class__) and self.parent == other.parent and check

    def _get_signature_parameters(self):
        return OrderedDict(inspect.signature(self.callback).parameters)

    async def _dispatch_error(self, ctx: BaseContext, error: Exception) -> None:
        ctx.bot.dispatch("application_command_error", ctx, error)


class SlashCommand(ApplicationCommand):
    """A class that implements the protocol for a slash command.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    This is a subclass of :class:`.Invokable`.

    .. versionadded:: 2.0

    Attributes
    -----------
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    options: List[:class:`Option`]
        The parameters for this command.
    parent: Optional[:class:`SlashCommandGroup`]
        The parent group that this command belongs to.
    guild_only: :class:`bool`
        Whether the command should only be usable inside a guild.
    default_member_permissions: :class:`~discord.Permissions`
        The default permissions a member needs to be able to run the command.
    name_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        The name localizations for this command. The values of this should be ``"locale": "name"``. See
        `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
    description_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        The description localizations for this command. The values of this should be ``"locale": "description"``.
        See `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
    """
    type = 1

    def __new__(cls, *args, **kwargs) -> SlashCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__(func, **kwargs)

        self.name_localizations: Optional[Dict[str, str]] = kwargs.get("name_localizations", None)
        _validate_names(self)

        description = kwargs.get("description") or (
            inspect.cleandoc(func.__doc__).splitlines()[0] if func.__doc__ is not None else "No description provided"
        )

        self.description: str = description
        self.description_localizations: Optional[Dict[str, str]] = kwargs.get("description_localizations", None)
        _validate_descriptions(self)

        self.attached_to_group: bool = False

        self.options: List[Option] = kwargs.get("options", [])

        self._cog = MISSING

    def _validate_parameters(self):
        params = self._get_signature_parameters()
        if kwop := self.options:
            self.options: List[Option] = self._match_option_param_names(params, kwop)
        else:
            self.options: List[Option] = self._parse_options(params)

    def _check_required_params(self, params):
        params = iter(params.items())
        required_params = (
            ["self", "context"]
            if self.attached_to_group
            or self.cog
            else ["context"]
        )
        for p in required_params:
            try:
                next(params)
            except StopIteration:
                raise ClientException(f'Callback for {self.name} command is missing "{p}" parameter.')

        return params

    def _parse_options(self, params, *, check_params: bool = True) -> List[Option]:
        if check_params:
            params = self._check_required_params(params)

        final_options = []
        for p_name, p_obj in params:
            option = p_obj.annotation
            if option == inspect.Parameter.empty:
                option = str

            if self._is_typing_union(option):
                if self._is_typing_optional(option):
                    option = Option(option.__args__[0], default=None)
                else:
                    option = Option(option.__args__)

            if not isinstance(option, Option):
                if isinstance(p_obj.default, Option):
                    p_obj.default.input_type = SlashCommandOptionType.from_datatype(option)
                    option = p_obj.default
                else:
                    option = Option(option)

            if option.default is None and not p_obj.default == inspect.Parameter.empty:
                if isinstance(p_obj.default, type) and issubclass(p_obj.default, (DiscordEnum, Enum)):
                    option = Option(p_obj.default)
                elif isinstance(p_obj.default, Option) and not (default := p_obj.default.default) is None:
                    option.default = default
                else:
                    option.default = p_obj.default
                    option.required = False
            if option.name is None:
                option.name = p_name
            if option.name != p_name or option._parameter_name is None:
                option._parameter_name = p_name

            _validate_names(option)
            _validate_descriptions(option)

            final_options.append(option)

        return final_options

    def _match_option_param_names(self, params, options):
        params = self._check_required_params(params)

        check_annotations: List[Callable[[Option, Type], bool]] = [
            lambda o, a: o.input_type == SlashCommandOptionType.string
            and o.converter is not None,  # pass on converters
            lambda o, a: isinstance(o.input_type, SlashCommandOptionType),  # pass on slash cmd option type enums
            lambda o, a: isinstance(o._raw_type, tuple) and a == Union[o._raw_type],  # type: ignore # union types
            lambda o, a: self._is_typing_optional(a) and not o.required and o._raw_type in a.__args__,  # optional
            lambda o, a: isinstance(a, type) and issubclass(a, o._raw_type),  # 'normal' types
        ]
        for o in options:
            _validate_names(o)
            _validate_descriptions(o)
            try:
                p_name, p_obj = next(params)
            except StopIteration:  # not enough params for all the options
                raise ClientException("Too many arguments passed to the options kwarg.")
            p_obj = p_obj.annotation

            if not any(check(o, p_obj) for check in check_annotations):
                raise TypeError(f"Parameter {p_name} does not match input type of {o.name}.")
            o._parameter_name = p_name

        left_out_params = OrderedDict()
        for k, v in params:
            left_out_params[k] = v
        options.extend(self._parse_options(left_out_params, check_params=False))

        return options

    def _is_typing_union(self, annotation):
        return getattr(annotation, "__origin__", None) is Union or type(annotation) is getattr(
            types, "UnionType", Union
        )  # type: ignore

    def _is_typing_optional(self, annotation):
        return self._is_typing_union(annotation) and type(None) in annotation.__args__  # type: ignore

    @property
    def cog(self):
        return self._cog

    @cog.setter
    def cog(self, val):
        self._cog = val
        self._validate_parameters()

    @property
    def is_subcommand(self) -> bool:
        return self.parent is not None
    
    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the slash command."""
        return f"</{self.qualified_name}:{self.id}>"
    
    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "options": [o.to_dict() for o in self.options],
        }
        if self.name_localizations is not None:
            as_dict["name_localizations"] = self.name_localizations
        if self.description_localizations is not None:
            as_dict["description_localizations"] = self.description_localizations
        if self.is_subcommand:
            as_dict["type"] = SlashCommandOptionType.sub_command.value

        if self.guild_only is not None:
            as_dict["dm_permission"] = not self.guild_only

        if self.default_member_permissions is not None:
            as_dict["default_member_permissions"] = self.default_member_permissions.value

        return as_dict

    async def _parse_arguments(self, ctx: ApplicationContext) -> None:
        ctx.args = [ctx] if self.cog is None else [self.cog, ctx]

        # TODO: Parse the args better
        kwargs = {}
        for arg in ctx.interaction.data.get("options", []):
            op = find(lambda x: x.name == arg["name"], self.options)
            if op is None:
                continue
            arg = arg["value"]

            # Checks if input_type is user, role or channel
            if op.input_type in (
                SlashCommandOptionType.user,
                SlashCommandOptionType.role,
                SlashCommandOptionType.channel,
                SlashCommandOptionType.attachment,
                SlashCommandOptionType.mentionable,
            ):
                resolved = ctx.interaction.data.get("resolved", {})
                if (
                    op.input_type in (SlashCommandOptionType.user, SlashCommandOptionType.mentionable)
                    and (_data := resolved.get("members", {}).get(arg)) is not None
                ):
                    # The option type is a user, we resolved a member from the snowflake and assigned it to _data
                    if (_user_data := resolved.get("users", {}).get(arg)) is not None:
                        # We resolved the user from the user id
                        _data["user"] = _user_data
                    cache_flag = ctx.interaction._state.member_cache_flags.interaction
                    arg = ctx.guild._get_and_update_member(_data, int(arg), cache_flag)
                elif op.input_type is SlashCommandOptionType.mentionable:
                    if (_data := resolved.get("users", {}).get(arg)) is not None:
                        arg = User(state=ctx.interaction._state, data=_data)
                    elif (_data := resolved.get("roles", {}).get(arg)) is not None:
                        arg = Role(state=ctx.interaction._state, data=_data, guild=ctx.guild)
                    else:
                        arg = Object(id=int(arg))
                elif (_data := resolved.get(f"{op.input_type.name}s", {}).get(arg)) is not None:
                    if op.input_type is SlashCommandOptionType.channel and (
                        int(arg) in ctx.guild._channels or int(arg) in ctx.guild._threads
                    ):
                        arg = ctx.guild.get_channel_or_thread(int(arg))
                        _data["_invoke_flag"] = True
                        arg._update(_data) if isinstance(arg, Thread) else arg._update(ctx.guild, _data)
                    else:
                        obj_type = None
                        kw = {}
                        if op.input_type is SlashCommandOptionType.user:
                            obj_type = User
                        elif op.input_type is SlashCommandOptionType.role:
                            obj_type = Role
                            kw["guild"] = ctx.guild
                        elif op.input_type is SlashCommandOptionType.channel:
                            # NOTE:
                            # This is a fallback in case the channel/thread is not found in the
                            # guild's channels/threads. For channels, if this fallback occurs, at the very minimum,
                            # permissions will be incorrect due to a lack of permission_overwrite data.
                            # For threads, if this fallback occurs, info like thread owner id, message count,
                            # flags, and more will be missing due to a lack of data sent by Discord.
                            obj_type = _threaded_guild_channel_factory(_data["type"])[0]
                            kw["guild"] = ctx.guild
                        elif op.input_type is SlashCommandOptionType.attachment:
                            obj_type = Attachment
                        arg = obj_type(state=ctx.interaction._state, data=_data, **kw)
                else:
                    # We couldn't resolve the object, so we just return an empty object
                    arg = Object(id=int(arg))

            elif op.input_type == SlashCommandOptionType.string and (converter := op.converter) is not None:
                from discord.ext.commands import Converter
                if isinstance(converter, Converter):
                    if isinstance(converter, type):
                        arg = await converter().convert(ctx, arg)
                    else:
                        arg = await converter.convert(ctx, arg)

            elif op._raw_type in (SlashCommandOptionType.integer,
                                  SlashCommandOptionType.number,
                                  SlashCommandOptionType.string,
                                  SlashCommandOptionType.boolean):
                pass

            elif issubclass(op._raw_type, Enum):
                if isinstance(arg, str) and arg.isdigit():
                    try:
                        arg = op._raw_type(int(arg))
                    except ValueError:
                        arg = op._raw_type(arg)
                elif choice := find(lambda c: c.value == arg, op.choices):
                    arg = getattr(op._raw_type, choice.name)

            kwargs[op._parameter_name] = arg

        for o in self.options:
            if o._parameter_name not in kwargs:
                kwargs[o._parameter_name] = o.default

        ctx.kwargs = kwargs

    async def invoke_autocomplete_callback(self, ctx: AutocompleteContext):
        values = {i.name: i.default for i in self.options}

        for op in ctx.interaction.data.get("options", []):
            if op.get("focused", False):
                option = find(lambda o: o.name == op["name"], self.options)
                values.update({i["name"]: i["value"] for i in ctx.interaction.data["options"]})
                ctx.command = self
                ctx.focused = option
                ctx.value = op.get("value")
                ctx.options = values

                if len(inspect.signature(option.autocomplete).parameters) == 2:
                    instance = getattr(option.autocomplete, "__self__", ctx.cog)
                    result = option.autocomplete(instance, ctx)
                else:
                    result = option.autocomplete(ctx)

                if asyncio.iscoroutinefunction(option.autocomplete):
                    result = await result

                choices = [o if isinstance(o, OptionChoice) else OptionChoice(o) for o in result][:25]
                return await ctx.interaction.response.send_autocomplete_result(choices=choices)


# TODO: implement with GroupMixin maybe
class SlashCommandGroup(ApplicationCommand):
    """A class that implements the protocol for a slash command group.

    These can be created manually, but they should be created via the
    decorator or functional interface.

    This is a subclass of :class:`.Invokable`.

    .. versionadded:: 2.0

    Attributes
    -----------
    description: Optional[:class:`str`]
        The description for the command.
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    parent: Optional[:class:`SlashCommandGroup`]
        The parent group that this group belongs to. ``None`` if there
        isn't one.
    guild_only: :class:`bool`
        Whether the command should only be usable inside a guild.
    default_member_permissions: :class:`~discord.Permissions`
        The default permissions a member needs to be able to run the command.
    name_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        The name localizations for this command. The values of this should be ``"locale": "name"``. See
        `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
    description_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        The description localizations for this command. The values of this should be ``"locale": "description"``.
        See `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
    """
    __initial_commands__: List[Union[SlashCommand, SlashCommandGroup]]
    type = 1

    def __new__(cls, *args, **kwargs) -> SlashCommandGroup:
        self = super().__new__(cls)
        self.__original_kwargs__ = kwargs.copy()

        self.__initial_commands__ = []
        for i, c in cls.__dict__.items():
            if isinstance(c, type) and SlashCommandGroup in c.__bases__:
                c = c(
                    c.__name__,
                    (
                        inspect.cleandoc(cls.__doc__).splitlines()[0]
                        if cls.__doc__ is not None
                        else "No description provided"
                    ),
                )
            if isinstance(c, (SlashCommand, SlashCommandGroup)):
                c.parent = self
                c.attached_to_group = True
                self.__initial_commands__.append(c)

        return self

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        guild_ids: Optional[List[int]] = None,
        parent: Optional[SlashCommandGroup] = None,
        **kwargs,
    ) -> None:
        self.name = str(name)
        self.description = description or "No description provided"
        validate_chat_input_name(self.name)
        validate_chat_input_description(self.description)
        self.input_type = SlashCommandOptionType.sub_command_group
        self.subcommands: List[Union[SlashCommand, SlashCommandGroup]] = self.__initial_commands__
        self.guild_ids = guild_ids
        self.parent = parent
        self.attached_to_group: bool = False
        self.checks = kwargs.get("checks", [])

        self._before_invoke = None
        self._after_invoke = None
        self.cog = None
        self.id = None

        # Permissions
        self.default_member_permissions: Optional["Permissions"] = kwargs.get("default_member_permissions", None)
        self.guild_only: Optional[bool] = kwargs.get("guild_only", None)

        self.name_localizations: Optional[Dict[str, str]] = kwargs.get("name_localizations", None)
        self.description_localizations: Optional[Dict[str, str]] = kwargs.get("description_localizations", None)

    @property
    def module(self) -> Optional[str]:
        return self.__module__

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "options": [c.to_dict() for c in self.subcommands],
        }
        if self.name_localizations is not None:
            as_dict["name_localizations"] = self.name_localizations
        if self.description_localizations is not None:
            as_dict["description_localizations"] = self.description_localizations

        if self.parent is not None:
            as_dict["type"] = self.input_type.value

        if self.guild_only is not None:
            as_dict["dm_permission"] = not self.guild_only

        if self.default_member_permissions is not None:
            as_dict["default_member_permissions"] = self.default_member_permissions.value

        return as_dict

    def add_command(self, command: SlashCommand) -> None:
        if command.cog is MISSING:
            command.cog = self.cog

        self.subcommands.append(command)

    def command(self, cls: Type[T] = SlashCommand, **kwargs) -> Callable[[Callable], SlashCommand]:
        def wrap(func) -> T:
            command = cls(func, parent=self, **kwargs)
            self.add_command(command)
            return command

        return wrap

    def create_subgroup(
        self,
        name: str,
        description: Optional[str] = None,
        guild_ids: Optional[List[int]] = None,
        **kwargs,
    ) -> SlashCommandGroup:
        """
        Creates a new subgroup for this SlashCommandGroup.

        Parameters
        ----------
        name: :class:`str`
            The name of the group to create.
        description: Optional[:class:`str`]
            The description of the group to create.
        guild_ids: Optional[List[:class:`int`]]
            A list of the IDs of each guild this group should be added to, making it a guild command.
            This will be a global command if ``None`` is passed.
        guild_only: :class:`bool`
            Whether the command should only be usable inside a guild.
        default_member_permissions: :class:`~discord.Permissions`
            The default permissions a member needs to be able to run the command.
        checks: List[Callable[[:class:`.ApplicationContext`], :class:`bool`]]
            A list of predicates that verifies if the command could be executed
            with the given :class:`.ApplicationContext` as the sole parameter. If an exception
            is necessary to be thrown to signal failure, then one inherited from
            :exc:`.ApplicationCommandError` should be used. Note that if the checks fail then
            :exc:`.CheckFailure` exception is raised to the :func:`.on_application_command_error`
            event.
        name_localizations: Optional[Dict[:class:`str`, :class:`str`]]
            The name localizations for this command. The values of this should be ``"locale": "name"``. See
            `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
        description_localizations: Optional[Dict[:class:`str`, :class:`str`]]
            The description localizations for this command. The values of this should be ``"locale": "description"``.
            See `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.

        Returns
        --------
        SlashCommandGroup
            The slash command group that was created.
        """

        if self.parent is not None:
            raise Exception("A command subgroup can only have commands and not any more groups.")

        sub_command_group = SlashCommandGroup(name, description, guild_ids, parent=self, **kwargs)
        self.subcommands.append(sub_command_group)
        return sub_command_group

    def subgroup(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        guild_ids: Optional[List[int]] = None,
    ) -> Callable[[Type[SlashCommandGroup]], SlashCommandGroup]:
        """A shortcut decorator that initializes the provided subclass of :class:`.SlashCommandGroup`
        as a subgroup.

        .. versionadded:: 2.0

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the group to create. This will resolve to the name of the decorated class if ``None`` is passed.
        description: Optional[:class:`str`]
            The description of the group to create.
        guild_ids: Optional[List[:class:`int`]]
            A list of the IDs of each guild this group should be added to, making it a guild command.
            This will be a global command if ``None`` is passed.

        Returns
        --------
        Callable[[Type[SlashCommandGroup]], SlashCommandGroup]
            The slash command group that was created.
        """

        def inner(cls: Type[SlashCommandGroup]) -> SlashCommandGroup:
            group = cls(
                name or cls.__name__,
                description
                or (
                    inspect.cleandoc(cls.__doc__).splitlines()[0]
                    if cls.__doc__ is not None
                    else "No description provided"
                ),
                guild_ids=guild_ids,
                parent=self,
            )
            self.subcommands.append(group)
            return group

        return inner

    async def invoke(self, ctx: ApplicationContext) -> None:
        option = ctx.interaction.data["options"][0]
        resolved = ctx.interaction.data.get("resolved", None)
        command = find(lambda x: x.name == option["name"], self.subcommands)
        option["resolved"] = resolved
        ctx.interaction.data = option
        ctx.invoked_subcommand = command
        await command.invoke(ctx)

    async def invoke_autocomplete_callback(self, ctx: AutocompleteContext) -> None:
        option = ctx.interaction.data["options"][0]
        command = find(lambda x: x.name == option["name"], self.subcommands)
        ctx.interaction.data = option
        await command.invoke_autocomplete_callback(ctx)

    def walk_commands(self) -> Generator[SlashCommand, None, None]:
        """An iterator that recursively walks through all slash commands in this group.

        Yields
        ------
        :class:`.SlashCommand`
            A slash command from the group.
        """
        for command in self.subcommands:
            if isinstance(command, SlashCommandGroup):
                yield from command.walk_commands()
            yield command

    def _set_cog(self, cog):
        super()._set_cog(cog)
        for subcommand in self.subcommands:
            subcommand._set_cog(cog)


class ContextMenuCommand(ApplicationCommand):
    """A base class that implements the protocol for context menu commands.

    These are not meant to be directly used, same as :class:`ApplicationCommand`.

    This is a subclass of :class:`.Invokable` but does not support the ``parent`` attribute.

    .. versionadded:: 2.0

    Attributes
    -----------
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    guild_only: :class:`bool`
        Whether the command should only be usable inside a guild.
    default_member_permissions: :class:`~discord.Permissions`
        The default permissions a member needs to be able to run the command.
    name_localizations: Optional[Dict[:class:`str`, :class:`str`]]
        The name localizations for this command. The values of this should be ``"locale": "name"``. See
        `here <https://discord.com/developers/docs/reference#locales>`_ for a list of valid locales.
    """

    def __new__(cls, *args, **kwargs) -> ContextMenuCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__(func, **kwargs)

        self.name_localizations: Optional[Dict[str, str]] = kwargs.get("name_localizations", None)

        # Discord API doesn't support setting descriptions for context menu commands, so it must be empty
        self.description = ""

        self.cog = None
        self.id = None

        self.validate_parameters()

        # Context Menu commands can't have parents
        self.parent = None

    def validate_parameters(self):
        params = self._get_signature_parameters()
        if list(params.items())[0][0] == "self":
            temp = list(params.items())
            temp.pop(0)
            params = dict(temp)
        params = iter(params)

        # next we have the 'ctx' as the next parameter
        try:
            next(params)
        except StopIteration:
            raise ClientException(f'Callback for {self.name} command is missing "ctx" parameter.')

        # next we have the 'user/message' as the next parameter
        try:
            next(params)
        except StopIteration:
            cmd = "user" if type(self) == UserCommand else "message"
            raise ClientException(f'Callback for {self.name} command is missing "{cmd}" parameter.')

        # next there should be no more parameters
        try:
            next(params)
            raise ClientException(f"Callback for {self.name} command has too many parameters.")
        except StopIteration:
            pass

    def to_dict(self) -> Dict[str, Union[str, int]]:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "type": self.type,
        }

        if self.guild_only is not None:
            as_dict["dm_permission"] = not self.guild_only

        if self.default_member_permissions is not None:
            as_dict["default_member_permissions"] = self.default_member_permissions.value

        if self.name_localizations is not None:
            as_dict["name_localizations"] = self.name_localizations

        return as_dict


class UserCommand(ContextMenuCommand):
    """A class that implements the protocol for user context menu commands.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    This is a subclass of :class:`.Invokable` but does not support the ``parent`` attribute.

    .. versionadded:: 2.0

    Attributes
    -----------
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    """
    type = 2

    def __new__(cls, *args, **kwargs) -> UserCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    async def _invoke(self, ctx: ApplicationContext) -> None:
        if "members" not in ctx.interaction.data["resolved"]:
            _data = ctx.interaction.data["resolved"]["users"]
            for i, v in _data.items():
                v["id"] = int(i)
                user = v
            target = User(state=ctx.interaction._state, data=user)
        else:
            _data = ctx.interaction.data["resolved"]["members"]
            for i, v in _data.items():
                v["id"] = int(i)
                member = v
            _data = ctx.interaction.data["resolved"]["users"]
            for i, v in _data.items():
                v["id"] = int(i)
                user = v
            member["user"] = user
            target = Member(
                data=member,
                guild=ctx.interaction._state._get_guild(ctx.interaction.guild_id),
                state=ctx.interaction._state,
            )

        if self.cog is not None:
            await self.callback(self.cog, ctx, target)
        else:
            await self.callback(ctx, target)


class MessageCommand(ContextMenuCommand):
    """A class that implements the protocol for message context menu commands.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    This is a subclass of :class:`.Invokable` but does not support the ``parent`` attribute.

    .. versionadded:: 2.0

    Attributes
    -----------
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    """
    type = 3

    def __new__(cls, *args, **kwargs) -> MessageCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    async def _invoke(self, ctx: ApplicationContext):
        _data = ctx.interaction.data["resolved"]["messages"]
        for i, v in _data.items():
            v["id"] = int(i)
            message = v
        channel = ctx.interaction._state.get_channel(int(message["channel_id"]))
        if channel is None:
            author_id = int(message["author"]["id"])
            self_or_system_message: bool = ctx.bot.user.id == author_id or try_enum(
                MessageType, message["type"]
            ) not in (
                MessageType.default,
                MessageType.reply,
                MessageType.application_command,
                MessageType.thread_starter_message,
            )
            user_id = ctx.author.id if self_or_system_message else author_id
            data = await ctx.interaction._state.http.start_private_message(user_id)
            channel = ctx.interaction._state.add_dm_channel(data)

        target = Message(state=ctx.interaction._state, channel=channel, data=message)

        if self.cog is not None:
            await self.callback(self.cog, ctx, target)
        else:
            await self.callback(ctx, target)


def slash_command(**kwargs):
    """Decorator for slash commands that invokes :func:`application_command`.

    .. versionadded:: 2.0

    Returns
    --------
    Callable[..., :class:`.SlashCommand`]
        A decorator that converts the provided method into a :class:`.SlashCommand`.
    """
    return application_command(cls=SlashCommand, **kwargs)


def user_command(**kwargs):
    """Decorator for user commands that invokes :func:`application_command`.

    .. versionadded:: 2.0

    Returns
    --------
    Callable[..., :class:`.UserCommand`]
        A decorator that converts the provided method into a :class:`.UserCommand`.
    """
    return application_command(cls=UserCommand, **kwargs)


def message_command(**kwargs):
    """Decorator for message commands that invokes :func:`application_command`.

    .. versionadded:: 2.0

    Returns
    --------
    Callable[..., :class:`.MessageCommand`]
        A decorator that converts the provided method into a :class:`.MessageCommand`.
    """
    return application_command(cls=MessageCommand, **kwargs)


def application_command(cls=SlashCommand, **attrs):
    """A decorator that transforms a function into an :class:`.ApplicationCommand`. More specifically,
    one of :class:`.SlashCommand`, :class:`.UserCommand`, or :class:`.MessageCommand`. The exact class
    depends on the ``cls`` parameter.
    
    The ``description`` and ``name`` of the command are automatically inferred from the function name
    and function docstring.

    .. versionadded:: 2.0

    Parameters
    -----------
    cls: :class:`.ApplicationCommand`
        The class to construct with. By default, this is :class:`.SlashCommand`.
        You usually do not change this.
    attrs
        Keyword arguments to pass into the construction of the class denoted
        by ``cls``.

    Raises
    -------
    TypeError
        If the function is not a coroutine or is already a command.

    Returns
    --------
    Callable[..., :class:`.ApplicationCommand`]
        A decorator that converts the provided method into an :class:`.ApplicationCommand`, or subclass of it.
    """

    def decorator(func: Callable) -> cls:
        if isinstance(func, ApplicationCommand):
            func = func.callback
        elif not callable(func):
            raise TypeError("func needs to be a callable or a subclass of ApplicationCommand.")
        return cls(func, **attrs)

    return decorator


def command(**kwargs):
    """An alias for :meth:`application_command`.

    .. note::
        This decorator is overridden by :func:`ext.commands.command`.

    .. versionadded:: 2.0

    Returns
    --------
    Callable[..., :class:`.ApplicationCommand`]
        A decorator that converts the provided method into an :class:`.ApplicationCommand`.
    """
    return application_command(**kwargs)


docs = "https://discord.com/developers/docs"
valid_locales = [
    "da",
    "de",
    "en-GB",
    "en-US",
    "es-ES",
    "fr",
    "hr",
    "it",
    "lt",
    "hu",
    "nl",
    "no",
    "pl",
    "pt-BR",
    "ro",
    "fi",
    "sv-SE",
    "vi",
    "tr",
    "cs",
    "el",
    "bg",
    "ru",
    "uk",
    "hi",
    "th",
    "zh-CN",
    "ja",
    "zh-TW",
    "ko",
]


# Validation
def validate_chat_input_name(name: Any, locale: Optional[str] = None):
    # Must meet the regex ^[-_\w\d\u0901-\u097D\u0E00-\u0E7F]{1,32}$
    if locale is not None and locale not in valid_locales:
        raise ValidationError(
            f"Locale '{locale}' is not a valid locale, see {docs}/reference#locales for list of supported locales."
        )
    error = None
    if not isinstance(name, str):
        error = TypeError(f'Command names and options must be of type str. Received "{name}"')
    elif not re.match(r"^[-_\w\d\u0901-\u097D\u0E00-\u0E7F]{1,32}$", name):
        error = ValidationError(
            r"Command names and options must follow the regex \"^[-_\w\d\u0901-\u097D\u0E00-\u0E7F]{1,32}$\". "
            f"For more information, see {docs}/interactions/application-commands#application-command-object-"
            f'application-command-naming. Received "{name}"'
        )
    elif name.lower() != name:  # Can't use islower() as it fails if none of the chars can be lowered. See #512.
        error = ValidationError(f'Command names and options must be lowercase. Received "{name}"')

    if error:
        if locale:
            error.args = (f"{error.args[0]} in locale {locale}",)
        raise error


def validate_chat_input_description(description: Any, locale: Optional[str] = None):
    if locale is not None and locale not in valid_locales:
        raise ValidationError(
            f"Locale '{locale}' is not a valid locale, see {docs}/reference#locales for list of supported locales."
        )
    error = None
    if not isinstance(description, str):
        error = TypeError(f'Command and option description must be of type str. Received "{description}"')
    elif not 1 <= len(description) <= 100:
        error = ValidationError(
            f'Command and option description must be 1-100 characters long. Received "{description}"'
        )

    if error:
        if locale:
            error.args = (f"{error.args[0]} in locale {locale}",)
        raise error
