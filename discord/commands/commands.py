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
import types
import functools
import inspect
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING

from ..enums import SlashCommandOptionType, ChannelType
from ..member import Member
from ..user import User
from ..message import Message
from .context import ApplicationContext, AutocompleteContext
from ..utils import find, get_or_fetch, async_all
from ..errors import ValidationError, ClientException
from .errors import ApplicationCommandError, CheckFailure, ApplicationCommandInvokeError
from .permissions import Permission

__all__ = (
    "_BaseCommand",
    "ApplicationCommand",
    "SlashCommand",
    "Option",
    "OptionChoice",
    "option",
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
    from ..interactions import Interaction

def wrap_callback(coro):
    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            ret = await coro(*args, **kwargs)
        except ApplicationCommandError:
            raise
        except asyncio.CancelledError:
            return
        except Exception as exc:
            raise ApplicationCommandInvokeError(exc) from exc
        return ret
    return wrapped

def hooked_wrapped_callback(command, ctx, coro):
    @functools.wraps(coro)
    async def wrapped(arg):
        try:
            ret = await coro(arg)
        except ApplicationCommandError:
            raise
        except asyncio.CancelledError:
            return
        except Exception as exc:
            raise ApplicationCommandInvokeError(exc) from exc
        finally:
            await command.call_after_hooks(ctx)
        return ret
    return wrapped

class _BaseCommand:
    __slots__ = ()

class ApplicationCommand(_BaseCommand):
    cog = None
    
    def __repr__(self):
        return f"<discord.commands.{self.__class__.__name__} name={self.name}>"

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    async def __call__(self, ctx, *args, **kwargs):
        """|coro|
        Calls the command's callback.

        This method bypasses all checks that a command has and does not
        convert the arguments beforehand, so take care to pass the correct
        arguments in.
        """
        return await self.callback(ctx, *args, **kwargs)

    async def prepare(self, ctx: ApplicationContext) -> None:
        # This should be same across all 3 types
        ctx.command = self

        if not await self.can_run(ctx):
            raise CheckFailure(f'The check functions for the command {self.name} failed')

        # TODO: Add cooldown

        await self.call_before_hooks(ctx)

    async def invoke(self, ctx: ApplicationContext) -> None:
        await self.prepare(ctx)

        injected = hooked_wrapped_callback(self, ctx, self._invoke)
        await injected(ctx)

    async def can_run(self, ctx: ApplicationContext) -> bool:

        if not await ctx.bot.can_run(ctx):
            raise CheckFailure(f'The global check functions for command {self.name} failed.')

        predicates = self.checks
        if not predicates:
            # since we have no checks, then we just return True.
            return True

        return await async_all(predicate(ctx) for predicate in predicates) # type: ignore    
    
    async def dispatch_error(self, ctx: ApplicationContext, error: Exception) -> None:
        ctx.command_failed = True
        cog = self.cog
        try:
            coro = self.on_error
        except AttributeError:
            pass
        else:
            injected = wrap_callback(coro)
            if cog is not None:
                await injected(cog, ctx, error)
            else:
                await injected(ctx, error)

        try:
            if cog is not None:
                local = cog.__class__._get_overridden_method(cog.cog_command_error)
                if local is not None:
                    wrapped = wrap_callback(local)
                    await wrapped(ctx, error)
        finally:
            ctx.bot.dispatch('application_command_error', ctx, error)

    def _get_signature_parameters(self):
        return OrderedDict(inspect.signature(self.callback).parameters)

    def error(self, coro):
        """A decorator that registers a coroutine as a local error handler.

        A local error handler is an :func:`.on_command_error` event limited to
        a single command. However, the :func:`.on_command_error` is still
        invoked afterwards as the catch-all.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the local error handler.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The error handler must be a coroutine.')

        self.on_error = coro
        return coro

    def has_error_handler(self) -> bool:
        """:class:`bool`: Checks whether the command has an error handler registered.
        """
        return hasattr(self, 'on_error')

    def before_invoke(self, coro):
        """A decorator that registers a coroutine as a pre-invoke hook.
        A pre-invoke hook is called directly before the command is
        called. This makes it a useful function to set up database
        connections or any type of set up required.
        This pre-invoke hook takes a sole parameter, a :class:`.Context`.
        See :meth:`.Bot.before_invoke` for more info.
        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the pre-invoke hook.
        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_invoke = coro
        return coro

    def after_invoke(self, coro):
        """A decorator that registers a coroutine as a post-invoke hook.
        A post-invoke hook is called directly after the command is
        called. This makes it a useful function to clean-up database
        connections or any type of clean up required.
        This post-invoke hook takes a sole parameter, a :class:`.Context`.
        See :meth:`.Bot.after_invoke` for more info.
        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the post-invoke hook.
        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_invoke = coro
        return coro

    async def call_before_hooks(self, ctx: ApplicationContext) -> None:
        # now that we're done preparing we can call the pre-command hooks
        # first, call the command local hook:
        cog = self.cog
        if self._before_invoke is not None:
            # should be cog if @commands.before_invoke is used
            instance = getattr(self._before_invoke, '__self__', cog)
            # __self__ only exists for methods, not functions
            # however, if @command.before_invoke is used, it will be a function
            if instance:
                await self._before_invoke(instance, ctx)  # type: ignore
            else:
                await self._before_invoke(ctx)  # type: ignore

        # call the cog local hook if applicable:
        if cog is not None:
            hook = cog.__class__._get_overridden_method(cog.cog_before_invoke)
            if hook is not None:
                await hook(ctx)

        # call the bot global hook if necessary
        hook = ctx.bot._before_invoke
        if hook is not None:
            await hook(ctx)

    async def call_after_hooks(self, ctx: ApplicationContext) -> None:
        cog = self.cog
        if self._after_invoke is not None:
            instance = getattr(self._after_invoke, '__self__', cog)
            if instance:
                await self._after_invoke(instance, ctx)  # type: ignore
            else:
                await self._after_invoke(ctx)  # type: ignore

        # call the cog local hook if applicable:
        if cog is not None:
            hook = cog.__class__._get_overridden_method(cog.cog_after_invoke)
            if hook is not None:
                await hook(ctx)

        hook = ctx.bot._after_invoke
        if hook is not None:
            await hook(ctx)

    @property
    def full_parent_name(self) -> str:
        """:class:`str`: Retrieves the fully qualified parent command name.

        This the base command name required to execute it. For example,
        in ``/one two three`` the parent name would be ``one two``.
        """
        entries = []
        command = self
        while command.parent is not None and hasattr(command.parent, "name"):
            command = command.parent
            entries.append(command.name)

        return ' '.join(reversed(entries))

    def qualified_name(self) -> str:
        """:class:`str`: Retrieves the fully qualified command name.

        This is the full parent name with the command name as well.
        For example, in ``/one two three`` the qualified name would be
        ``one two three``.
        """

        parent = self.full_parent_name

        if parent:
            return parent + ' ' + self.name
        else:
            return self.name

class SlashCommand(ApplicationCommand):
    r"""A class that implements the protocol for a slash command.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    -----------
    name: :class:`str`
        The name of the command.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the command is called.
    description: Optional[:class:`str`]
        The description for the command.
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    options: List[:class:`Option`]
        The parameters for this command.
    parent: Optional[:class:`SlashCommandGroup`]
        The parent group that this command belongs to. ``None`` if there
        isn't one.
    default_permission: :class:`bool`
        Whether the command is enabled by default when it is added to a guild.
    permissions: List[:class:`Permission`]
        The permissions for this command.

        .. note::

            If this is not empty then default_permissions will be set to False.    

    cog: Optional[:class:`Cog`]
        The cog that this command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationContext`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationContext` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_application_command_error`
        event.
    """
    type = 1

    def __new__(cls, *args, **kwargs) -> SlashCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        self.callback = func

        self.guild_ids: Optional[List[int]] = kwargs.get("guild_ids", None)

        name = kwargs.get("name") or func.__name__
        validate_chat_input_name(name)
        self.name: str = name
        self.id = None

        description = kwargs.get("description") or (
            inspect.cleandoc(func.__doc__).splitlines()[0]
            if func.__doc__ is not None
            else "No description provided"
        )
        validate_chat_input_description(description)
        self.description: str = description
        self.parent = kwargs.get('parent')
        self.is_subcommand: bool = self.parent is not None

        self.cog = None

        params = self._get_signature_parameters()
        self.options: List[Option] = kwargs.get('options') or self._parse_options(params)

        try:
            checks = func.__commands_checks__
            checks.reverse()
        except AttributeError:
            checks = kwargs.get('checks', [])

        self.checks = checks

        self._before_invoke = None
        self._after_invoke = None

        # Permissions
        self.default_permission = kwargs.get("default_permission", True)
        self.permissions: List[Permission] = getattr(func, "__app_cmd_perms__", []) + kwargs.get("permissions", [])
        if self.permissions and self.default_permission:
            self.default_permission = False


    def _parse_options(self, params) -> List[Option]:
        final_options = []

        if list(params.items())[0][0] == "self":
            temp = list(params.items())
            temp.pop(0)
            params = dict(temp)
        params = iter(params.items())

        # next we have the 'ctx' as the next parameter
        try:
            next(params)
        except StopIteration:
            raise ClientException(
                f'Callback for {self.name} command is missing "ctx" parameter.'
            )

        final_options = []

        for p_name, p_obj in params:

            option = p_obj.annotation
            if option == inspect.Parameter.empty:
                option = str

            if self._is_typing_union(option):
                if self._is_typing_optional(option):
                    option = Option(
                        option.__args__[0], "No description provided", required=False
                    )
                else:
                    option = Option(
                        option.__args__, "No description provided"
                    )

            if not isinstance(option, Option):
                option = Option(option, "No description provided")
                if p_obj.default != inspect.Parameter.empty:
                    option.required = False

            option.default = option.default if option.default is not None else p_obj.default

            if option.default == inspect.Parameter.empty:
                option.default = None

            if option.name is None:
                option.name = p_name
            option._parameter_name = p_name

            final_options.append(option)

        return final_options

    def _is_typing_union(self, annotation):
        return (
            getattr(annotation, '__origin__', None) is Union
            or type(annotation) is getattr(types, "UnionType", Union)
        ) # type: ignore

    def _is_typing_optional(self, annotation):
        return self._is_typing_union(annotation) and type(None) in annotation.__args__  # type: ignore

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "options": [o.to_dict() for o in self.options],
            "default_permission": self.default_permission,
        }
        if self.is_subcommand:
            as_dict["type"] = SlashCommandOptionType.sub_command.value

        return as_dict

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, SlashCommand)
            and other.name == self.name
            and other.description == self.description
        )

    async def _invoke(self, ctx: ApplicationContext) -> None:
        # TODO: Parse the args better
        kwargs = {}
        for arg in ctx.interaction.data.get("options", []):
            op = find(lambda x: x.name == arg["name"], self.options)
            arg = arg["value"]

            # Checks if input_type is user, role or channel
            if (
                SlashCommandOptionType.user.value
                <= op.input_type.value
                <= SlashCommandOptionType.role.value
            ):
                name = "member" if op.input_type.name == "user" else op.input_type.name
                arg = await get_or_fetch(ctx.guild, name, int(arg), default=int(arg))

            elif op.input_type == SlashCommandOptionType.mentionable:
                arg_id = int(arg)
                arg = await get_or_fetch(ctx.guild, "member", arg_id)
                if arg is None:
                    arg = ctx.guild.get_role(arg_id) or arg_id

            elif op.input_type == SlashCommandOptionType.string and op._converter is not None:
                arg = await op._converter.convert(ctx, arg)

            kwargs[op._parameter_name] = arg

        for o in self.options:
            if o._parameter_name not in kwargs:
                kwargs[o._parameter_name] = o.default
        
        if self.cog is not None:
            await self.callback(self.cog, ctx, **kwargs)
        else:
            await self.callback(ctx, **kwargs)

    async def invoke_autocomplete_callback(self, ctx: AutocompleteContext):
        values = { i.name: i.default for i in self.options }
        
        for op in ctx.interaction.data.get("options", []):
            if op.get("focused", False):
                option = find(lambda o: o.name == op["name"], self.options)
                values.update({
                    i["name"]:i["value"] 
                    for i in ctx.interaction.data["options"]
                })
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
                    
                choices = [
                    o if isinstance(o, OptionChoice) else OptionChoice(o)
                    for o in result
                ][:25]
                return await ctx.interaction.response.send_autocomplete_result(choices=choices)


    def copy(self):
        """Creates a copy of this command.

        Returns
        --------
        :class:`SlashCommand`
            A new instance of this command.
        """
        ret = self.__class__(self.callback, **self.__original_kwargs__)
        return self._ensure_assignment_on_copy(ret)

    def _ensure_assignment_on_copy(self, other):
        other._before_invoke = self._before_invoke
        other._after_invoke = self._after_invoke
        if self.checks != other.checks:
            other.checks = self.checks.copy()
        #if self._buckets.valid and not other._buckets.valid:
        #    other._buckets = self._buckets.copy()
        #if self._max_concurrency != other._max_concurrency:
        #    # _max_concurrency won't be None at this point
        #    other._max_concurrency = self._max_concurrency.copy()  # type: ignore

        try:
            other.on_error = self.on_error
        except AttributeError:
            pass
        return other

    def _update_copy(self, kwargs: Dict[str, Any]):
        if kwargs:
            kw = kwargs.copy()
            kw.update(self.__original_kwargs__)
            copy = self.__class__(self.callback, **kw)
            return self._ensure_assignment_on_copy(copy)
        else:
            return self.copy()

channel_type_map = {
    'TextChannel': ChannelType.text,
    'VoiceChannel': ChannelType.voice,
    'StageChannel': ChannelType.stage_voice,
    'CategoryChannel': ChannelType.category
}

class Option:
    def __init__(
        self, input_type: Any, /, description: str = None, **kwargs
    ) -> None:
        self.name: Optional[str] = kwargs.pop("name", None)
        self.description = description or "No description provided"
        self._converter = None
        self.channel_types: List[SlashCommandOptionType] = kwargs.pop("channel_types", [])
        if not isinstance(input_type, SlashCommandOptionType):
            if hasattr(input_type, "convert"):
                self._converter = input_type
                input_type = SlashCommandOptionType.string
            else:
                _type = SlashCommandOptionType.from_datatype(input_type)
                if _type == SlashCommandOptionType.channel:
                    if not isinstance(input_type, tuple):
                        input_type = (input_type,)
                    for i in input_type:
                        if i.__name__ == 'GuildChannel':
                            continue

                        channel_type = channel_type_map[i.__name__]
                        self.channel_types.append(channel_type)
                input_type = _type
        self.input_type = input_type
        self.required: bool = kwargs.pop("required", True)
        self.choices: List[OptionChoice] = [
            o if isinstance(o, OptionChoice) else OptionChoice(o)
            for o in kwargs.pop("choices", list())
        ]
        self.default = kwargs.pop("default", None)

        if self.input_type == SlashCommandOptionType.integer:
            minmax_types = (int, type(None))
        elif self.input_type == SlashCommandOptionType.number:
            minmax_types = (int, float, type(None))
        else:
            minmax_types = (type(None),)
        minmax_typehint = Optional[Union[minmax_types]] # type: ignore

        self.min_value: minmax_typehint = kwargs.pop("min_value", None)
        self.max_value: minmax_typehint = kwargs.pop("max_value", None)
        
        if not (isinstance(self.min_value, minmax_types) or self.min_value is None):
            raise TypeError(f"Expected {minmax_typehint} for min_value, got \"{type(self.min_value).__name__}\"")
        if not (isinstance(self.max_value, minmax_types) or self.min_value is None):
            raise TypeError(f"Expected {minmax_typehint} for max_value, got \"{type(self.max_value).__name__}\"")

        self.autocomplete = kwargs.pop("autocomplete", None)

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "type": self.input_type.value,
            "required": self.required,
            "choices": [c.to_dict() for c in self.choices],
            "autocomplete": bool(self.autocomplete)
        }
        if self.channel_types:
            as_dict["channel_types"] = [t.value for t in self.channel_types]
        if self.min_value is not None:
            as_dict["min_value"] = self.min_value
        if self.max_value is not None:
            as_dict["max_value"] = self.max_value

        return as_dict


    def __repr__(self):
        return f"<discord.commands.{self.__class__.__name__} name={self.name}>"


class OptionChoice:
    def __init__(self, name: str, value: Optional[Union[str, int, float]] = None):
        self.name = name
        self.value = value or name

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        return {"name": self.name, "value": self.value}

def option(name, type=None, **kwargs):
    """A decorator that can be used instead of typehinting Option"""
    def decor(func):
        nonlocal type
        type = type or func.__annotations__.get(name, str)
        func.__annotations__[name] = Option(type, **kwargs)
        return func
    return decor

class SlashCommandGroup(ApplicationCommand, Option):
    r"""A class that implements the protocol for a slash command group.

    These can be created manually, but they should be created via the
    decorator or functional interface.

    Attributes
    -----------
    name: :class:`str`
        The name of the command.
    description: Optional[:class:`str`]
        The description for the command.
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    parent: Optional[:class:`SlashCommandGroup`]
        The parent group that this group belongs to. ``None`` if there
        isn't one.
    subcommands: List[Union[:class:`SlashCommand`, :class:`SlashCommandGroup`]]
        The list of all subcommands under this group.
    cog: Optional[:class:`Cog`]
        The cog that this command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationContext`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationContext` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_application_command_error`
        event.
    """
    type = 1

    def __new__(cls, *args, **kwargs) -> SlashCommandGroup:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(
        self,
        name: str,
        description: str,
        guild_ids: Optional[List[int]] = None,
        parent: Optional[SlashCommandGroup] = None,
        **kwargs
    ) -> None:
        validate_chat_input_name(name)
        validate_chat_input_description(description)
        super().__init__(
            SlashCommandOptionType.sub_command_group,
            name=name,
            description=description,
        )
        self.subcommands: List[Union[SlashCommand, SlashCommandGroup]] = []
        self.guild_ids = guild_ids
        self.parent = parent
        self.checks = []

        self._before_invoke = None
        self._after_invoke = None
        self.cog = None

        # Permissions
        self.default_permission = kwargs.get("default_permission", True)
        self.permissions: List[Permission] = kwargs.get("permissions", [])
        if self.permissions and self.default_permission:
            self.default_permission = False

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "options": [c.to_dict() for c in self.subcommands],
        }

        if self.parent is not None:
            as_dict["type"] = self.input_type.value

        return as_dict

    def command(self, **kwargs) -> SlashCommand:
        def wrap(func) -> SlashCommand:
            command = SlashCommand(func, parent=self, **kwargs)
            self.subcommands.append(command)
            return command

        return wrap

    def command_group(self, name, description) -> SlashCommandGroup:
        if self.parent is not None:
            # TODO: Improve this error message
            raise Exception("Subcommands can only be nested once")

        sub_command_group = SlashCommandGroup(name, description, parent=self)
        self.subcommands.append(sub_command_group)
        return sub_command_group

    async def _invoke(self, ctx: ApplicationContext) -> None:
        option = ctx.interaction.data["options"][0]
        command = find(lambda x: x.name == option["name"], self.subcommands)
        ctx.interaction.data = option
        await command.invoke(ctx)

    async def invoke_autocomplete_callback(self, ctx: AutocompleteContext) -> None:
        option = ctx.interaction.data["options"][0]
        command = find(lambda x: x.name == option["name"], self.subcommands)
        ctx.interaction.data = option
        await command.invoke_autocomplete_callback(ctx)


class ContextMenuCommand(ApplicationCommand):
    r"""A class that implements the protocol for context menu commands.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    -----------
    name: :class:`str`
        The name of the command.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the command is called.
    guild_ids: Optional[List[:class:`int`]]
        The ids of the guilds where this command will be registered.
    cog: Optional[:class:`Cog`]
        The cog that this command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationContext`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationContext` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_application_command_error`
        event.
    """
    def __new__(cls, *args, **kwargs) -> ContextMenuCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        self.callback = func

        self.guild_ids: Optional[List[int]] = kwargs.get("guild_ids", None)

        # Discord API doesn't support setting descriptions for context menu commands
        # so it must be empty
        self.description = ""
        self.name: str = kwargs.pop("name", func.__name__)
        if not isinstance(self.name, str):
            raise TypeError("Name of a command must be a string.")

        self.cog = None

        try:
            checks = func.__commands_checks__
            checks.reverse()
        except AttributeError:
            checks = kwargs.get('checks', [])

        self.checks = checks
        self._before_invoke = None
        self._after_invoke = None
        
        self.validate_parameters()

        # Context Menu commands don't have permissions
        self.permissions = []

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
            raise ClientException(
                f'Callback for {self.name} command is missing "ctx" parameter.'
            )

        # next we have the 'user/message' as the next parameter
        try:
            next(params)
        except StopIteration:
            cmd = "user" if type(self) == UserCommand else "message"
            raise ClientException(
                f'Callback for {self.name} command is missing "{cmd}" parameter.'
            )

        # next there should be no more parameters
        try:
            next(params)
            raise ClientException(
                f"Callback for {self.name} command has too many parameters."
            )
        except StopIteration:
            pass
    
    def qualified_name(self):
        return self.name

    def to_dict(self) -> Dict[str, Union[str, int]]:
        return {"name": self.name, "description": self.description, "type": self.type}


class UserCommand(ContextMenuCommand):
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

    def copy(self):
        """Creates a copy of this command.

        Returns
        --------
        :class:`UserCommand`
            A new instance of this command.
        """
        ret = self.__class__(self.callback, **self.__original_kwargs__)
        return self._ensure_assignment_on_copy(ret)

    def _ensure_assignment_on_copy(self, other):
        other._before_invoke = self._before_invoke
        other._after_invoke = self._after_invoke
        if self.checks != other.checks:
            other.checks = self.checks.copy()
        #if self._buckets.valid and not other._buckets.valid:
        #    other._buckets = self._buckets.copy()
        #if self._max_concurrency != other._max_concurrency:
        #    # _max_concurrency won't be None at this point
        #    other._max_concurrency = self._max_concurrency.copy()  # type: ignore

        try:
            other.on_error = self.on_error
        except AttributeError:
            pass
        return other

    def _update_copy(self, kwargs: Dict[str, Any]):
        if kwargs:
            kw = kwargs.copy()
            kw.update(self.__original_kwargs__)
            copy = self.__class__(self.callback, **kw)
            return self._ensure_assignment_on_copy(copy)
        else:
            return self.copy()


class MessageCommand(ContextMenuCommand):
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
            data = await ctx.interaction._state.http.start_private_message(
                int(message["author"]["id"])
            )
            channel = ctx.interaction._state.add_dm_channel(data)

        target = Message(state=ctx.interaction._state, channel=channel, data=message)
        
        if self.cog is not None:
            await self.callback(self.cog, ctx, target)
        else:
            await self.callback(ctx, target)
    
    def copy(self):
        """Creates a copy of this command.

        Returns
        --------
        :class:`MessageCommand`
            A new instance of this command.
        """
        ret = self.__class__(self.callback, **self.__original_kwargs__)
        return self._ensure_assignment_on_copy(ret)

    def _ensure_assignment_on_copy(self, other):
        other._before_invoke = self._before_invoke
        other._after_invoke = self._after_invoke
        if self.checks != other.checks:
            other.checks = self.checks.copy()
        #if self._buckets.valid and not other._buckets.valid:
        #    other._buckets = self._buckets.copy()
        #if self._max_concurrency != other._max_concurrency:
        #    # _max_concurrency won't be None at this point
        #    other._max_concurrency = self._max_concurrency.copy()  # type: ignore

        try:
            other.on_error = self.on_error
        except AttributeError:
            pass
        return other

    def _update_copy(self, kwargs: Dict[str, Any]):
        if kwargs:
            kw = kwargs.copy()
            kw.update(self.__original_kwargs__)
            copy = self.__class__(self.callback, **kw)
            return self._ensure_assignment_on_copy(copy)
        else:
            return self.copy()

def slash_command(**kwargs):
    """Decorator for slash commands that invokes :func:`application_command`.
    .. versionadded:: 2.0
    Returns
    --------
    Callable[..., :class:`SlashCommand`]
        A decorator that converts the provided method into a :class:`.SlashCommand`.
    """
    return application_command(cls=SlashCommand, **kwargs)

def user_command(**kwargs):
    """Decorator for user commands that invokes :func:`application_command`.
    .. versionadded:: 2.0
    Returns
    --------
    Callable[..., :class:`UserCommand`]
        A decorator that converts the provided method into a :class:`.UserCommand`.
    """
    return application_command(cls=UserCommand, **kwargs)

def message_command(**kwargs):
    """Decorator for message commands that invokes :func:`application_command`.
    .. versionadded:: 2.0
    Returns
    --------
    Callable[..., :class:`MessageCommand`]
        A decorator that converts the provided method into a :class:`.MessageCommand`.
    """
    return application_command(cls=MessageCommand, **kwargs)

def application_command(cls=SlashCommand, **attrs):
    """A decorator that transforms a function into an :class:`.ApplicationCommand`. More specifically,
    usually one of :class:`.SlashCommand`, :class:`.UserCommand`, or :class:`.MessageCommand`. The exact class
    depends on the ``cls`` parameter.
    By default the ``description`` attribute is received automatically from the
    docstring of the function and is cleaned up with the use of
    ``inspect.cleandoc``. If the docstring is ``bytes``, then it is decoded
    into :class:`str` using utf-8 encoding.
    The ``name`` attribute also defaults to the function name unchanged.
    .. versionadded:: 2.0
    Parameters
    -----------
    cls: :class:`.ApplicationCommand`
        The class to construct with. By default this is :class:`.SlashCommand`.
        You usually do not change this.
    attrs
        Keyword arguments to pass into the construction of the class denoted
        by ``cls``.
    Raises
    -------
    TypeError
        If the function is not a coroutine or is already a command.
    """

    def decorator(func: Callable) -> cls:
        if isinstance(func, ApplicationCommand):
            func = func.callback
        elif not callable(func):
            raise TypeError(
                "func needs to be a callable or a subclass of ApplicationCommand."
            )
        return cls(func, **attrs)

    return decorator

def command(**kwargs):
    """There is an alias for :meth:`application_command`.
    .. note::
        This decorator is overridden by :func:`commands.command`.
    .. versionadded:: 2.0
    Returns
    --------
    Callable[..., :class:`ApplicationCommand`]
        A decorator that converts the provided method into an :class:`.ApplicationCommand`.
    """
    return application_command(**kwargs)

# Validation
def validate_chat_input_name(name: Any):
    if not isinstance(name, str):
        raise TypeError("Name of a command must be a string.")
    if " " in name:
        raise ValidationError("Name of a chat input command cannot have spaces.")
    if not name.islower():
        raise ValidationError("Name of a chat input command must be lowercase.")
    if len(name) > 32 or len(name) < 1:
        raise ValidationError(
            "Name of a chat input command must be less than 32 characters and non empty."
        )


def validate_chat_input_description(description: Any):
    if not isinstance(description, str):
        raise TypeError("Description of a command must be a string.")
    if len(description) > 100 or len(description) < 1:
        raise ValidationError(
            "Description of a chat input command must be less than 100 characters and non empty."
        )
