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
import datetime
import functools
import inspect
import re
import types
from collections import OrderedDict
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
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
    overload,
)

from ..enums import ChannelType, SlashCommandOptionType
from ..errors import ClientException, ValidationError
from ..member import Member
from ..message import Attachment, Message
from ..user import User
from ..utils import async_all, find, get_or_fetch, utcnow
from .context import ApplicationContext, AutocompleteContext
from .errors import ApplicationCommandError, ApplicationCommandInvokeError, CheckFailure
from .options import Option, OptionChoice
from .permissions import CommandPermission

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
    from typing_extensions import Concatenate, ParamSpec

    from ..cog import Cog

T = TypeVar("T")
CogT = TypeVar("CogT", bound="Cog")
Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])

if TYPE_CHECKING:
    P = ParamSpec("P")
else:
    P = TypeVar("P")


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
            if hasattr(command, "_max_concurrency") and command._max_concurrency is not None:
                await command._max_concurrency.release(ctx)
            await command.call_after_hooks(ctx)
        return ret

    return wrapped


def unwrap_function(function: Callable[..., Any]) -> Callable[..., Any]:
    partial = functools.partial
    while True:
        if hasattr(function, "__wrapped__"):
            function = function.__wrapped__
        elif isinstance(function, partial):
            function = function.func
        else:
            return function


class _BaseCommand:
    __slots__ = ()


class ApplicationCommand(_BaseCommand, Generic[CogT, P, T]):
    cog = None

    def __init__(self, func: Callable, **kwargs) -> None:
        from ..ext.commands.cooldowns import BucketType, CooldownMapping, MaxConcurrency

        try:
            cooldown = func.__commands_cooldown__
        except AttributeError:
            cooldown = kwargs.get("cooldown")

        if cooldown is None:
            buckets = CooldownMapping(cooldown, BucketType.default)
        elif isinstance(cooldown, CooldownMapping):
            buckets = cooldown
        else:
            raise TypeError("Cooldown must be a an instance of CooldownMapping or None.")
        self._buckets: CooldownMapping = buckets

        try:
            max_concurrency = func.__commands_max_concurrency__
        except AttributeError:
            max_concurrency = kwargs.get("max_concurrency")

        self._max_concurrency: Optional[MaxConcurrency] = max_concurrency

        self._callback = None
        self.module = None

    def __repr__(self) -> str:
        return f"<discord.commands.{self.__class__.__name__} name={self.name}>"

    def __eq__(self, other) -> bool:
        if hasattr(self, "id") and hasattr(other, "id"):
            check = self.id == other.id
        else:
            check = self.name == other.name and self.guild_ids == self.guild_ids
        return isinstance(other, self.__class__) and self.parent == other.parent and check

    async def __call__(self, ctx, *args, **kwargs):
        """|coro|
        Calls the command's callback.

        This method bypasses all checks that a command has and does not
        convert the arguments beforehand, so take care to pass the correct
        arguments in.
        """
        return await self.callback(ctx, *args, **kwargs)

    @property
    def callback(
        self,
    ) -> Union[
        Callable[Concatenate[CogT, ApplicationContext, P], Coro[T]],
        Callable[Concatenate[ApplicationContext, P], Coro[T]],
    ]:
        return self._callback

    @callback.setter
    def callback(
        self,
        function: Union[
            Callable[Concatenate[CogT, ApplicationContext, P], Coro[T]],
            Callable[Concatenate[ApplicationContext, P], Coro[T]],
        ],
    ) -> None:
        self._callback = function
        unwrap = unwrap_function(function)
        self.module = unwrap.__module__

    def _prepare_cooldowns(self, ctx: ApplicationContext):
        if self._buckets.valid:
            current = datetime.datetime.now().timestamp()
            bucket = self._buckets.get_bucket(ctx, current)  # type: ignore # ctx instead of non-existent message

            if bucket is not None:
                retry_after = bucket.update_rate_limit(current)

                if retry_after:
                    from ..ext.commands.errors import CommandOnCooldown

                    raise CommandOnCooldown(bucket, retry_after, self._buckets.type)  # type: ignore

    async def prepare(self, ctx: ApplicationContext) -> None:
        # This should be same across all 3 types
        ctx.command = self

        if not await self.can_run(ctx):
            raise CheckFailure(f"The check functions for the command {self.name} failed")

        if hasattr(self, "_max_concurrency"):
            if self._max_concurrency is not None:
                # For this application, context can be duck-typed as a Message
                await self._max_concurrency.acquire(ctx)  # type: ignore # ctx instead of non-existent message

            try:
                self._prepare_cooldowns(ctx)
                await self.call_before_hooks(ctx)
            except:
                if self._max_concurrency is not None:
                    await self._max_concurrency.release(ctx)  # type: ignore # ctx instead of non-existent message
                raise

    def is_on_cooldown(self, ctx: ApplicationContext) -> bool:
        """Checks whether the command is currently on cooldown.

        .. note::

            This uses the current time instead of the interaction time.

        Parameters
        -----------
        ctx: :class:`.ApplicationContext`
            The invocation context to use when checking the commands cooldown status.

        Returns
        --------
        :class:`bool`
            A boolean indicating if the command is on cooldown.
        """
        if not self._buckets.valid:
            return False

        bucket = self._buckets.get_bucket(ctx)
        current = utcnow().timestamp()
        return bucket.get_tokens(current) == 0

    def reset_cooldown(self, ctx: ApplicationContext) -> None:
        """Resets the cooldown on this command.

        Parameters
        -----------
        ctx: :class:`.ApplicationContext`
            The invocation context to reset the cooldown under.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx)  # type: ignore # ctx instead of non-existent message
            bucket.reset()

    def get_cooldown_retry_after(self, ctx: ApplicationContext) -> float:
        """Retrieves the amount of seconds before this command can be tried again.

        .. note::

            This uses the current time instead of the interaction time.

        Parameters
        -----------
        ctx: :class:`.ApplicationContext`
            The invocation context to retrieve the cooldown from.

        Returns
        --------
        :class:`float`
            The amount of time left on this command's cooldown in seconds.
            If this is ``0.0`` then the command isn't on cooldown.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx)
            current = utcnow().timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    async def invoke(self, ctx: ApplicationContext) -> None:
        await self.prepare(ctx)

        injected = hooked_wrapped_callback(self, ctx, self._invoke)
        await injected(ctx)

    async def can_run(self, ctx: ApplicationContext) -> bool:

        if not await ctx.bot.can_run(ctx):
            raise CheckFailure(f"The global check functions for command {self.name} failed.")

        predicates = self.checks
        if not predicates:
            # since we have no checks, then we just return True.
            return True

        return await async_all(predicate(ctx) for predicate in predicates)  # type: ignore

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
            ctx.bot.dispatch("application_command_error", ctx, error)

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
            raise TypeError("The error handler must be a coroutine.")

        self.on_error = coro
        return coro

    def has_error_handler(self) -> bool:
        """:class:`bool`: Checks whether the command has an error handler registered."""
        return hasattr(self, "on_error")

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
            raise TypeError("The pre-invoke hook must be a coroutine.")

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
            raise TypeError("The post-invoke hook must be a coroutine.")

        self._after_invoke = coro
        return coro

    async def call_before_hooks(self, ctx: ApplicationContext) -> None:
        # now that we're done preparing we can call the pre-command hooks
        # first, call the command local hook:
        cog = self.cog
        if self._before_invoke is not None:
            # should be cog if @commands.before_invoke is used
            instance = getattr(self._before_invoke, "__self__", cog)
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
            instance = getattr(self._after_invoke, "__self__", cog)
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
    def cooldown(self):
        return self._buckets._cooldown

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

        return " ".join(reversed(entries))

    @property
    def qualified_name(self) -> str:
        """:class:`str`: Retrieves the fully qualified command name.

        This is the full parent name with the command name as well.
        For example, in ``/one two three`` the qualified name would be
        ``one two three``.
        """

        parent = self.full_parent_name

        if parent:
            return f"{parent} {self.name}"
        else:
            return self.name

    def __str__(self) -> str:
        return self.qualified_name

    def _set_cog(self, cog):
        self.cog = cog


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
    permissions: List[:class:`CommandPermission`]
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
    cooldown: Optional[:class:`~discord.ext.commands.Cooldown`]
        The cooldown applied when the command is invoked. ``None`` if the command
        doesn't have a cooldown.

        .. versionadded:: 2.0
    """
    type = 1

    def __new__(cls, *args, **kwargs) -> SlashCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__(func, **kwargs)
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")
        self.callback = func

        self.guild_ids: Optional[List[int]] = kwargs.get("guild_ids", None)

        name = kwargs.get("name") or func.__name__
        validate_chat_input_name(name)
        self.name: str = name
        self.id = None

        description = kwargs.get("description") or (
            inspect.cleandoc(func.__doc__).splitlines()[0] if func.__doc__ is not None else "No description provided"
        )
        validate_chat_input_description(description)
        self.description: str = description
        self.parent = kwargs.get("parent")
        self.attached_to_group: bool = False

        self.cog = None

        params = self._get_signature_parameters()
        if kwop := kwargs.get("options", None):
            self.options: List[Option] = self._match_option_param_names(params, kwop)
        else:
            self.options: List[Option] = self._parse_options(params)

        try:
            checks = func.__commands_checks__
            checks.reverse()
        except AttributeError:
            checks = kwargs.get("checks", [])

        self.checks = checks

        self._before_invoke = None
        self._after_invoke = None

        # Permissions
        self.default_permission = kwargs.get("default_permission", True)
        self.permissions: List[CommandPermission] = getattr(func, "__app_cmd_perms__", []) + kwargs.get(
            "permissions", []
        )
        if self.permissions and self.default_permission:
            self.default_permission = False

    def _parse_options(self, params) -> List[Option]:
        if list(params.items())[0][0] == "self":
            temp = list(params.items())
            temp.pop(0)
            params = dict(temp)
        params = iter(params.items())

        # next we have the 'ctx' as the next parameter
        try:
            next(params)
        except StopIteration:
            raise ClientException(f'Callback for {self.name} command is missing "ctx" parameter.')

        final_options = []
        for p_name, p_obj in params:

            option = p_obj.annotation
            if option == inspect.Parameter.empty:
                option = str

            if self._is_typing_union(option):
                if self._is_typing_optional(option):
                    option = Option(option.__args__[0], "No description provided", required=False)
                else:
                    option = Option(option.__args__, "No description provided")

            if not isinstance(option, Option):
                option = Option(option, "No description provided")

            if option.default is None:
                if p_obj.default == inspect.Parameter.empty:
                    option.default = None
                else:
                    option.default = p_obj.default
                    option.required = False

            if option.name is None:
                option.name = p_name
            option._parameter_name = p_name

            validate_chat_input_name(option.name)
            validate_chat_input_description(option.description)

            final_options.append(option)

        return final_options

    def _match_option_param_names(self, params, options):
        if list(params.items())[0][0] == "self":
            temp = list(params.items())
            temp.pop(0)
            params = dict(temp)
        params = iter(params.items())

        # next we have the 'ctx' as the next parameter
        try:
            next(params)
        except StopIteration:
            raise ClientException(f'Callback for {self.name} command is missing "ctx" parameter.')

        check_annotations = [
            lambda o, a: o.input_type == SlashCommandOptionType.string
            and o.converter is not None,  # pass on converters
            lambda o, a: isinstance(o.input_type, SlashCommandOptionType),  # pass on slash cmd option type enums
            lambda o, a: isinstance(o._raw_type, tuple) and a == Union[o._raw_type],  # type: ignore # union types
            lambda o, a: self._is_typing_optional(a) and not o.required and o._raw_type in a.__args__,  # optional
            lambda o, a: inspect.isclass(a) and issubclass(a, o._raw_type),  # 'normal' types
        ]
        for o in options:
            validate_chat_input_name(o.name)
            validate_chat_input_description(o.description)
            try:
                p_name, p_obj = next(params)
            except StopIteration:  # not enough params for all the options
                raise ClientException(f"Too many arguments passed to the options kwarg.")
            p_obj = p_obj.annotation

            if not any(c(o, p_obj) for c in check_annotations):
                raise TypeError(f"Parameter {p_name} does not match input type of {o.name}.")
            o._parameter_name = p_name

        left_out_params = OrderedDict()
        left_out_params[""] = ""  # bypass first iter (ctx)
        for k, v in params:
            left_out_params[k] = v
        options.extend(self._parse_options(left_out_params))

        return options

    def _is_typing_union(self, annotation):
        return getattr(annotation, "__origin__", None) is Union or type(annotation) is getattr(
            types, "UnionType", Union
        )  # type: ignore

    def _is_typing_optional(self, annotation):
        return self._is_typing_union(annotation) and type(None) in annotation.__args__  # type: ignore

    @property
    def is_subcommand(self) -> bool:
        return self.parent is not None

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

    async def _invoke(self, ctx: ApplicationContext) -> None:
        # TODO: Parse the args better
        kwargs = {}
        for arg in ctx.interaction.data.get("options", []):
            op = find(lambda x: x.name == arg["name"], self.options)
            arg = arg["value"]

            # Checks if input_type is user, role or channel
            if SlashCommandOptionType.user.value <= op.input_type.value <= SlashCommandOptionType.role.value:
                if ctx.guild is None and op.input_type.name == "user":
                    _data = ctx.interaction.data["resolved"]["users"][arg]
                    _data["id"] = int(arg)
                    arg = User(state=ctx.interaction._state, data=_data)
                else:
                    name = "member" if op.input_type.name == "user" else op.input_type.name
                    arg = await get_or_fetch(ctx.guild, name, int(arg), default=int(arg))

            elif op.input_type == SlashCommandOptionType.mentionable:
                arg_id = int(arg)
                arg = await get_or_fetch(ctx.guild, "member", arg_id)
                if arg is None:
                    arg = ctx.guild.get_role(arg_id) or arg_id

            elif op.input_type == SlashCommandOptionType.string and (converter := op.converter) is not None:
                arg = await converter.convert(converter, ctx, arg)

            elif op.input_type == SlashCommandOptionType.attachment:
                _data = ctx.interaction.data["resolved"]["attachments"][arg]
                _data["id"] = int(arg)
                arg = Attachment(state=ctx.interaction._state, data=_data)

            kwargs[op._parameter_name] = arg

        for o in self.options:
            if o._parameter_name not in kwargs:
                kwargs[o._parameter_name] = o.default

        if self.cog is not None:
            await self.callback(self.cog, ctx, **kwargs)
        elif self.parent is not None and self.attached_to_group is True:
            await self.callback(self.parent, ctx, **kwargs)
        else:
            await self.callback(ctx, **kwargs)

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
        # if self._buckets.valid and not other._buckets.valid:
        #    other._buckets = self._buckets.copy()
        # if self._max_concurrency != other._max_concurrency:
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


class SlashCommandGroup(ApplicationCommand):
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
        description: str,
        guild_ids: Optional[List[int]] = None,
        parent: Optional[SlashCommandGroup] = None,
        **kwargs,
    ) -> None:
        validate_chat_input_name(name)
        validate_chat_input_description(description)
        self.name = name
        self.description = description
        self.input_type = SlashCommandOptionType.sub_command_group
        self.subcommands: List[Union[SlashCommand, SlashCommandGroup]] = self.__initial_commands__
        self.guild_ids = guild_ids
        self.parent = parent
        self.checks = []

        self._before_invoke = None
        self._after_invoke = None
        self.cog = None
        self.id = None

        # Permissions
        self.default_permission = kwargs.get("default_permission", True)
        self.permissions: List[CommandPermission] = kwargs.get("permissions", [])
        if self.permissions and self.default_permission:
            self.default_permission = False

    @property
    def module(self) -> Optional[str]:
        return self.__module__

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "options": [c.to_dict() for c in self.subcommands],
            "default_permission": self.default_permission,
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

    def create_subgroup(
        self,
        name: str,
        description: Optional[str] = None,
        guild_ids: Optional[List[int]] = None,
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

        Returns
        --------
        SlashCommandGroup
            The slash command group that was created.
        """

        if self.parent is not None:
            # TODO: Improve this error message
            raise Exception("Subcommands can only be nested once")

        sub_command_group = SlashCommandGroup(name, description, guild_ids, parent=self)
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

    async def _invoke(self, ctx: ApplicationContext) -> None:
        option = ctx.interaction.data["options"][0]
        resolved = ctx.interaction.data.get("resolved", None)
        command = find(lambda x: x.name == option["name"], self.subcommands)
        option["resolved"] = resolved
        ctx.interaction.data = option
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

    def copy(self):
        """Creates a copy of this command group.

        Returns
        --------
        :class:`SlashCommandGroup`
            A new instance of this command group.
        """
        ret = self.__class__(
            name=self.name,
            description=self.description,
            **self.__original_kwargs__,
        )
        return self._ensure_assignment_on_copy(ret)

    def _ensure_assignment_on_copy(self, other):
        other.parent = self.parent

        other._before_invoke = self._before_invoke
        other._after_invoke = self._after_invoke

        if self.subcommands != other.subcommands:
            other.subcommands = self.subcommands.copy()

        if self.checks != other.checks:
            other.checks = self.checks.copy()

        return other

    def _update_copy(self, kwargs: Dict[str, Any]):
        if kwargs:
            kw = kwargs.copy()
            kw.update(self.__original_kwargs__)
            copy = self.__class__(self.callback, **kw)
            return self._ensure_assignment_on_copy(copy)
        else:
            return self.copy()

    def _set_cog(self, cog):
        self.cog = cog
        for subcommand in self.subcommands:
            subcommand._set_cog(cog)


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
    default_permission: :class:`bool`
        Whether the command is enabled by default when it is added to a guild.
    permissions: List[:class:`.CommandPermission`]
        The permissions for this command.

        .. note::
            If this is not empty then default_permissions will be set to ``False``.

    cog: Optional[:class:`Cog`]
        The cog that this command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.ApplicationContext`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.ApplicationContext` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_application_command_error`
        event.
    cooldown: Optional[:class:`~discord.ext.commands.Cooldown`]
        The cooldown applied when the command is invoked. ``None`` if the command
        doesn't have a cooldown.

        .. versionadded:: 2.0
    """

    def __new__(cls, *args, **kwargs) -> ContextMenuCommand:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__(func, **kwargs)
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
        self.id = None

        try:
            checks = func.__commands_checks__
            checks.reverse()
        except AttributeError:
            checks = kwargs.get("checks", [])

        self.checks = checks
        self._before_invoke = None
        self._after_invoke = None

        self.validate_parameters()

        self.default_permission = kwargs.get("default_permission", True)
        self.permissions: List[CommandPermission] = getattr(func, "__app_cmd_perms__", []) + kwargs.get(
            "permissions", []
        )
        if self.permissions and self.default_permission:
            self.default_permission = False

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

    @property
    def qualified_name(self):
        return self.name

    def to_dict(self) -> Dict[str, Union[str, int]]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "default_permission": self.default_permission,
        }


class UserCommand(ContextMenuCommand):
    r"""A class that implements the protocol for user context menu commands.

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
        # if self._buckets.valid and not other._buckets.valid:
        #    other._buckets = self._buckets.copy()
        # if self._max_concurrency != other._max_concurrency:
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
    r"""A class that implements the protocol for message context menu commands.

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
            data = await ctx.interaction._state.http.start_private_message(int(message["author"]["id"]))
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
        # if self._buckets.valid and not other._buckets.valid:
        #    other._buckets = self._buckets.copy()
        # if self._max_concurrency != other._max_concurrency:
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
            raise TypeError("func needs to be a callable or a subclass of ApplicationCommand.")
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


docs = "https://discord.com/developers/docs"


# Validation
def validate_chat_input_name(name: Any):
    # Must meet the regex ^[\w-]{1,32}$
    if not isinstance(name, str):
        raise TypeError(f"Chat input command names and options must be of type str. Received {name}")
    if not re.match(r"^[\w-]{1,32}$", name):
        raise ValidationError(
            r'Chat input command names and options must follow the regex "^[\w-]{1,32}$". For more information, see '
            f"{docs}/interactions/application-commands#application-command-object-application-command-naming. Received "
            f"{name}"
        )
    if not 1 <= len(name) <= 32:
        raise ValidationError(f"Chat input command names and options must be 1-32 characters long. Received {name}")
    if not name.lower() == name:  # Can't use islower() as it fails if none of the chars can be lower. See #512.
        raise ValidationError(f"Chat input command names and options must be lowercase. Received {name}")


def validate_chat_input_description(description: Any):
    if not isinstance(description, str):
        raise TypeError(f"Command description must be of type str. Received {description}")
    if not 1 <= len(description) <= 100:
        raise ValidationError(f"Command description must be 1-100 characters long. Received {description}")
