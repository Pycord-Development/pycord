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
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Generic, TypeVar, Union

from .. import abc, utils
from ..errors import (
    ApplicationCommandError,
    CheckFailure,
    CommandError,
    CommandInvokeError,
    CommandOnCooldown,
    DisabledCommand,
)
from .cooldowns import BucketType, Cooldown, CooldownMapping, MaxConcurrency

T = TypeVar("T")
BotT = TypeVar("BotT", bound="Union[Bot, AutoShardedBot]")
CogT = TypeVar("CogT", bound="Cog")

Coro = Coroutine[Any, Any, T]
MaybeCoro = Union[T, Coro[T]]

Check = Union[
    Callable[[CogT, "BaseContext"], MaybeCoro[bool]],
    Callable[["BaseContext"], MaybeCoro[bool]],
]

Error = Union[
    Callable[[CogT, "BaseContext[Any]", CommandError], Coro[Any]],
    Callable[["BaseContext[Any]", CommandError], Coro[Any]],
]
ErrorT = TypeVar("ErrorT", bound="Error")

Hook = Union[
    Callable[[CogT, "BaseContext"], Coro[Any]], Callable[["BaseContext"], Coro[Any]]
]
HookT = TypeVar("HookT", bound="Hook")

if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec

    from ..abc import MessageableChannel
    from ..bot import AutoShardedBot, Bot
    from ..cog import Cog
    from ..guild import Guild
    from ..interactions import Interaction
    from ..member import Member
    from ..message import Message
    from ..state import ConnectionState
    from ..user import ClientUser, User
    from ..voice_client import VoiceProtocol

    P = ParamSpec("P")

    Callback = (
        Callable[Concatenate[CogT, "BaseContext", P], Coro[T]]
        | Callable[Concatenate["BaseContext", P], Coro[T]]
    )
else:
    P = TypeVar("P")
    Callback = TypeVar("Callback")


__all__ = (
    "Invokable",
    "_BaseCommand",
    "BaseContext",
)


def unwrap_function(function: functools.partial | Callable) -> Callback:
    while True:
        if hasattr(function, "__wrapped__"):
            function = getattr(function, "__wrapped__")
        elif isinstance(function, functools.partial):
            function = function.func
        else:
            return function


def wrap_callback(coro: Callback):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            ret = await coro(*args, **kwargs)
        except CommandError:
            raise
        except asyncio.CancelledError:
            return
        except Exception as exc:
            raise CommandInvokeError(exc) from exc
        return ret

    return wrapper


def hook_wrapped_callback(command: Invokable, ctx: BaseContext, coro: Callback):
    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            ret = await coro(*args, **kwargs)
        except (ApplicationCommandError, CommandError):
            ctx.command_failed = True
            raise
        except asyncio.CancelledError:
            ctx.command_failed = True
            return
        except Exception as exc:
            ctx.command_failed = True
            raise CommandInvokeError(exc) from exc
        finally:
            if command._max_concurrency is not None:
                await command._max_concurrency.release(ctx)
            await command.call_after_hooks(ctx)

        return ret

    return wrapper


class _BaseCommand:
    __slots__ = ()


class BaseContext(abc.Messageable, Generic[BotT]):
    r"""A base class to provide ***basic & common functionality*** between
    :class:`.ApplicationContext` and :class:`~ext.commands.Context`.

    This is a subclass of :class:`~abc.Messageable` and can be used to
    send messages, etc.

    .. versionadded:: 2.2

    Attributes
    ----------
    bot: :class:`.Bot`
        The bot that contains the command being executed.
    command: Optional[:class:`Invokable`]
        The command that is being invoked currently.
    args: :class:`list`
        The list of transformed arguments that were passed into the command.
        If this is accessed during the :func:`.on_command_error` event
        then this list could be incomplete.
    kwargs: :class:`dict`
        A dictionary of transformed arguments that were passed into the command.
        Similar to :attr:`args`\, if this is accessed in the
        :func:`.on_command_error` event then this dict could be incomplete.
    invoked_with: Optional[:class:`str`]
        The command name that triggered this invocation. Useful for finding out
        which alias called the command.
    invoked_parents: List[:class:`str`]
        The command names of the parents that triggered this invocation. Useful for
        finding out which aliases called the command.

        For example in commands ``?a b c test``, the invoked parents are ``['a', 'b', 'c']``.
    invoked_subcommand: Optional[:class:`Invokable`]
        The subcommand that was invoked.
        If no valid subcommand was invoked then this is equal to ``None``.
    subcommand_passed: Optional[:class:`str`]
        The string that was attempted to call a subcommand. This does not have
        to point to a valid registered subcommand and could just point to a
        nonsense string. If nothing was passed to attempt a call to a
        subcommand then this is set to ``None``.

        .. note::

            This will always be ``None`` if accessed on through a slash command.

    command_failed: :class:`bool`
        A boolean that indicates if the command failed to be parsed, checked,
        or invoked.
    """

    def __init__(
        self,
        bot: Bot,
        command: Invokable | None,
        args: list[Any] = utils.MISSING,
        kwargs: dict[str, Any] = utils.MISSING,
        *,
        invoked_with: str | None = None,
        invoked_parents: list[str] = utils.MISSING,
        invoked_subcommand: Invokable | None = None,
        subcommand_passed: str | None = None,
        command_failed: bool = False,
    ):
        self.bot: Bot = bot
        self.command: Invokable | None = command
        self.args: list[Any] = args or []
        self.kwargs: dict[str, Any] = kwargs or {}

        self.invoked_with: str | None = invoked_with
        if not self.invoked_with and command:
            self.invoked_with = command.name

        self.invoked_parents: list[str] = invoked_parents or []
        if not self.invoked_parents and command:
            self.invoked_parents = [i.name for i in command.parents]

        # This will always be None for slash commands
        self.subcommand_passed: str | None = subcommand_passed

        self.invoked_subcommand: Invokable | None = invoked_subcommand
        self.command_failed: bool = command_failed

    async def invoke(
        self, command: Invokable[CogT, P, T], /, *args: P.args, **kwargs: P.kwargs
    ) -> T:
        r"""|coro|

        Invokes a command with the arguments given.

        This is useful if you want to just call the callback that a
        :class:`.Invokable` holds internally.

        .. note::

            This does not handle converters, checks, cooldowns, before-invoke,
            or after-invoke hooks in any matter. It calls the internal callback
            directly as-if it was a regular function.

            You must take care in passing the proper arguments when
            using this function.

        Parameters
        -----------
        command: :class:`.Invokable`
            The command that is going to be called.
        \*args
            The arguments to use.
        \*\*kwargs
            The keyword arguments to use.

        Raises
        -------
        TypeError
            The command argument to invoke is missing.
        """
        return await command(self, *args, **kwargs)

    async def _get_channel(self) -> abc.Messageable:
        return self.channel

    @property
    def source(self) -> Message | Interaction:
        """Property to return a message or interaction
        depending on the context.
        """
        raise NotImplementedError

    @property
    def _state(self) -> ConnectionState:
        return self.source._state

    @property
    def cog(self) -> Cog | None:
        """Returns the cog associated with this context's command.
        ``None`` if it does not exist.
        """
        if self.command is None:
            return None
        return self.command.cog

    @utils.cached_property
    def guild(self) -> Guild | None:
        """Returns the guild associated with this context's command.
        Shorthand for :attr:`.Interaction.guild`.
        """
        return self.source.guild

    @utils.cached_property
    def guild_id(self) -> int | None:
        """Returns the ID of the guild associated with this context's command.
        Shorthand for :attr:`.Interaction.guild_id`.
        """
        return getattr(self.source, "guild_id", self.guild.id if self.guild else None)

    @utils.cached_property
    def channel(self) -> MessageableChannel:
        """Union[:class:`.abc.Messageable`]: Returns the channel associated with this context's command."""
        return self.source.channel

    @utils.cached_property
    def channel_id(self) -> int | None:
        """Returns the ID of the channel associated with this context's command.
        Shorthand for :attr:`.Interaction.channel_id`.
        """
        return getattr(
            self.source, "channel_id", self.channel.id if self.channel else None
        )

    @utils.cached_property
    def author(self) -> User | Member:
        """Returns the user that sent this context's command.
        Shorthand for :attr:`.Interaction.user`.
        """
        return self.source.author

    @property
    def user(self) -> User | Member:
        """Alias for :attr:`BaseContext.author`."""
        return self.author

    @utils.cached_property
    def me(self) -> Member | ClientUser:
        """Similar to :attr:`.Guild.me` except it may return the :class:`.ClientUser`
        in private message contexts, or when :meth:`.Intents.guilds` is absent.
        """
        # bot.user will never be None at this point.
        return self.guild.me if self.guild and self.guild.me else self.bot.user  # type: ignore

    @property
    def voice_client(self) -> VoiceProtocol | None:
        """Returns the voice client associated with this context's command."""
        return self.guild.voice_client if self.guild else None


class Invokable(Generic[CogT, P, T]):
    r"""A base class to provide ***basic & common functionality*** between
    :class:`.ApplicationCommand` and :class:`~ext.commands.Command`.

    .. versionadded:: 2.2

    Attributes
    ----------
    name: str
        The name of the invokable/command.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the command is called.
    parent: Optional[:class:`Invokable`]
        The parent group of this command.
    cog: Optional[:class:`Cog`]
        The cog that this command belongs to. ``None`` if there isn't one.
    enabled: :class:`bool`
        A boolean that indicates if the command is currently enabled.
        If the command is invoked while it is disabled, then
        :exc:`.DisabledCommand` is raised to the :func:`.on_command_error`
        event. Defaults to ``True``.
    checks: List[Callable[[:class:`.BaseContext`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed with the given
        :class:`.BaseContext` (:class:`.ApplicationContext` or :class:`~ext.commands.Context`
        to be specific) as the sole parameter. If an exception is necessary to be thrown to
        signal failure, then one inherited from :exc:`.CommandError` should be used. Note that
        if the checks fail then :exc:`.CheckFailure` exception is raised to the :func:`.on_command_error`
        event.
    cooldown_after_parsing: :class:`bool`
        If ``True``\, cooldown processing is done after argument parsing,
        which calls converters. If ``False`` then cooldown processing is done
        first and then the converters are called second. Defaults to ``False``.
    cooldown: Optional[:class:`Cooldown`]
        The cooldown applied when the command is invoked.
    """
    __original_kwargs__: dict[str, Any]

    def __new__(cls, *args, **kwargs) -> Invokable:
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(
        self,
        func: Callback,
        name: str | None = None,
        enabled: bool = False,
        cooldown_after_parsing: bool = False,
        parent: Invokable | None = None,
        checks: list[Check] = [],
        cooldown: CooldownMapping | None = None,
        max_concurrency: MaxConcurrency | None = None,
    ):
        self.callback: Callback = func
        self.parent: Invokable | None = (
            parent if isinstance(parent, _BaseCommand) else None
        )
        self.cog: CogT | None = None
        self.module: Any = None

        self.name: str = str(name or func.__name__)
        self.enabled: bool = enabled
        self.cooldown_after_parsing: bool = cooldown_after_parsing

        # checks
        if _checks := getattr(func, "__commands_checks__", []):
            # combine all that we find (kwargs or decorator)
            _checks.reverse()
            checks += _checks

        self.checks: list[Check] = checks

        # cooldowns
        cooldown = getattr(func, "__commands_cooldown__", cooldown)

        if cooldown is None:
            buckets = CooldownMapping(cooldown, BucketType.default)
        elif isinstance(cooldown, CooldownMapping):
            buckets = cooldown
        else:
            raise TypeError(
                "Cooldown must be a an instance of CooldownMapping or None."
            )

        self._buckets: CooldownMapping = buckets

        # max concurrency
        self._max_concurrency: MaxConcurrency | None = getattr(
            func, "__commands_max_concurrency__", max_concurrency
        )

        # hooks
        self._before_invoke: Hook | None = None
        if hook := getattr(func, "__before_invoke__", None):
            self.before_invoke(hook)

        self._after_invoke: Hook | None = None
        if hook := getattr(func, "__after_invoke__", None):
            self.after_invoke(hook)

        self.on_error: Error | None

    @property
    def callback(self) -> Callback:
        """Returns the command's callback."""
        return self._callback

    @callback.setter
    def callback(self, func: Callback) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")

        self._callback = func
        unwrap = unwrap_function(func)
        self.module = unwrap.__module__

    @property
    def cooldown(self) -> Cooldown | None:
        """Returns the cooldown for the command."""
        return self._buckets._cooldown

    @property
    def qualified_name(self) -> str:
        """Retrieves the fully qualified command name.

        This is the full name of the parent command with the subcommand name as well.
        For example, in ``?one two three``, the qualified name would be
        ``one two three``.
        """
        if not self.parent:
            return self.name

        return f"{self.parent.qualified_name} {self.name}"

    @property
    def cog_name(self) -> str | None:
        """Optional[:class:`str`]: The name of the cog this command belongs to, if any."""
        return type(self.cog).__cog_name__ if self.cog is not None else None

    @property
    def parents(self) -> list[Invokable]:
        """List[:class:`Invokable`]: Retrieves the parents of this command.

        If the command has no parents then it returns an empty :class:`list`.

        For example in commands ``?a b c test``, the parents are ``[c, b, a]``.
        """
        entries = []
        command = self
        while command.parent is not None:
            command = command.parent
            entries.append(command)

        return entries

    @property
    def root_parent(self) -> Invokable | None:
        """Optional[:class:`Invokable`]: Retrieves the root parent of this command.

        If the command has no parents then it returns ``None``.

        For example in commands ``?a b c test``, the root parent is ``a``.
        """
        if not self.parent:
            return None
        return self.parents[-1]

    @property
    def full_parent_name(self) -> str | None:
        """Retrieves the fully qualified parent command name.

        This the base command name required to execute it. For example,
        in ``/one two three`` the parent name would be ``one two``.
        """
        if self.parent:
            return self.parent.qualified_name

    def __str__(self) -> str:
        return self.qualified_name

    async def __call__(self, ctx: BaseContext, *args: P.args, **kwargs: P.kwargs):
        """|coro|

        Calls the internal callback that the command holds.

        .. note::

            This bypasses all mechanisms -- including checks, converters,
            invoke hooks, cooldowns, etc. You must take care to pass
            the proper arguments and types to this function.
        """
        new_args = (ctx, *args)
        if self.cog is not None:
            new_args = (self.cog, *args)
        return await self.callback(*new_args, **kwargs)

    def update(self, **kwargs: Any) -> None:
        """Updates the :class:`Invokable` instance with updated attribute.

        Similar to creating a new instance except it updates the current.
        """
        self.__init__(self.callback, **dict(self.__original_kwargs__, **kwargs))

    def has_error_handler(self) -> bool:
        """Checks whether the command has an error handler registered."""
        return hasattr(self, "on_error")

    def before_invoke(self, coro: HookT) -> HookT:
        """A decorator that registers a coroutine as a pre-invoke hook.

        A pre-invoke hook is called directly before the command is
        called. This makes it a useful function to set up database
        connections or any type of set up required.

        This pre-invoke hook takes a sole parameter, a :class:`.BaseContext`.
        See :meth:`.Bot.before_invoke` for more info.

        Parameters
        ----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the pre-invoke hook.

        Raises
        ------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("The pre-invoke hook must be a coroutine.")

        self._before_invoke = coro
        return coro

    def after_invoke(self, coro: HookT) -> HookT:
        """A decorator that registers a coroutine as a post-invoke hook.

        A post-invoke hook is called directly after the command is
        called. This makes it a useful function to clean-up database
        connections or any type of clean up required.

        This post-invoke hook takes a sole parameter, a :class:`.BaseContext`.

        See :meth:`.Bot.after_invoke` for more info.

        Parameters
        ----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the post-invoke hook.

        Raises
        ------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("The post-invoke hook must be a coroutine.")

        self._after_invoke = coro
        return coro

    async def can_run(self, ctx: BaseContext) -> bool:
        """|coro|

        Checks if the command can be executed by checking all the predicates
        inside the :attr:`~Command.checks` attribute. This also checks whether the
        command is disabled.

        .. versionchanged:: 1.3
            Checks whether the command is disabled or not

        Parameters
        ----------
        ctx: :class:`.Context`
            The ctx of the command currently being invoked.

        Returns
        -------
        :class:`bool`
            A boolean indicating if the command can be invoked.

        Raises
        ------
        :class:`CommandError`
            Any command error that was raised during a check call will be propagated
            by this function.
        """
        if not self.enabled:
            raise DisabledCommand(f"{self.name} command is disabled")

        original = ctx.command
        ctx.command = self

        try:
            if not await ctx.bot.can_run(ctx):
                raise CheckFailure(
                    f"The global check functions for command {self.qualified_name} failed."
                )

            if (cog := self.cog) and (
                local_check := cog._get_overridden_method(cog.cog_check)
            ):
                ret = await utils.maybe_coroutine(local_check, ctx)
                if not ret:
                    return False

            predicates = self.checks
            if not predicates:
                # since we have no checks, then we just return True.
                return True

            return await utils.async_all(predicate(ctx) for predicate in predicates)
        finally:
            ctx.command = original

    def add_check(self, func: Check) -> None:
        """Adds a check to the command.

        This is the non-decorator interface to :func:`.check`.

        Parameters
        ----------
        func: Callable
            The function that will be used as a check.
        """

        self.checks.append(func)

    def remove_check(self, func: Check) -> None:
        """Removes a check from the command.

        This function is idempotent and will not raise an exception
        if the function is not in the command's checks.

        Parameters
        ----------
        func: Callable
            The function to remove from the checks.
        """

        try:
            self.checks.remove(func)
        except ValueError:
            pass

    def copy(self):
        """Creates a copy of this command.

        Returns
        -------
        :class:`Invokable`
            A new instance of this command.
        """
        ret = self.__class__(self.callback, **self.__original_kwargs__)
        return self._ensure_assignment_on_copy(ret)

    def _ensure_assignment_on_copy(self, other: Invokable):
        other._before_invoke = self._before_invoke
        other._after_invoke = self._after_invoke
        if self.checks != other.checks:
            other.checks = self.checks.copy()
        if self._buckets.valid and not other._buckets.valid:
            other._buckets = self._buckets.copy()
        if self._max_concurrency != other._max_concurrency:
            # _max_concurrency won't be None at this point
            other._max_concurrency = self._max_concurrency.copy()  # type: ignore

        try:
            other.on_error = self.on_error
        except AttributeError:
            pass
        return other

    def _update_copy(self, kwargs: dict[str, Any]):
        if kwargs:
            kw = kwargs.copy()
            kw.update(self.__original_kwargs__)
            copy = self.__class__(self.callback, **kw)
            return self._ensure_assignment_on_copy(copy)
        else:
            return self.copy()

    def _set_cog(self, cog: CogT):
        self.cog = cog

    def is_on_cooldown(self, ctx: BaseContext) -> bool:
        """Checks whether the command is currently on cooldown.

        .. note::

            This uses the current time instead of the interaction time.

        Parameters
        ----------
        ctx: :class:`.BaseContext`
            The invocation context to use when checking the command's cooldown status.

        Returns
        -------
        :class:`bool`
            A boolean indicating if the command is on cooldown.
        """
        if not self._buckets.valid:
            return False

        bucket = self._buckets.get_bucket(ctx)
        current = utils.utcnow().timestamp()
        return bucket.get_tokens(current) == 0

    def reset_cooldown(self, ctx) -> None:
        """Resets the cooldown on this command.

        Parameters
        ----------
        ctx: :class:`.BaseContext`
            The invocation context to reset the cooldown under.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx)  # type: ignore # ctx instead of non-existent message
            bucket.reset()

    def get_cooldown_retry_after(self, ctx) -> float:
        """Retrieves the amount of seconds before this command can be tried again.

        .. note::

            This uses the current time instead of the interaction time.

        Parameters
        ----------
        ctx: :class:`.BaseContext`
            The invocation context to retrieve the cooldown from.

        Returns
        -------
        :class:`float`
            The amount of time left on this command's cooldown in seconds.
            If this is ``0.0`` then the command isn't on cooldown.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(ctx)
            current = utils.utcnow().timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    def _prepare_cooldowns(self, ctx: BaseContext):
        if not self._buckets.valid:
            return

        current = datetime.datetime.now().timestamp()
        bucket = self._buckets.get_bucket(ctx, current)  # type: ignore # ctx instead of non-existent message

        if bucket:
            retry_after = bucket.update_rate_limit(current)

            if retry_after:
                raise CommandOnCooldown(bucket, retry_after, self._buckets.type)  # type: ignore

    async def call_before_hooks(self, ctx: BaseContext) -> None:
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

    async def call_after_hooks(self, ctx: BaseContext) -> None:
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

    async def _parse_arguments(self, ctx: BaseContext) -> None:
        """Parses arguments and attaches them to the context class (Union[:class:`~ext.commands.Context`, :class:`.ApplicationContext`])"""
        raise NotImplementedError

    async def prepare(self, ctx: BaseContext) -> None:
        ctx.command = self

        if not await self.can_run(ctx):
            raise CheckFailure(
                f"The check functions for command {self.qualified_name} failed."
            )

        if self._max_concurrency is not None:
            # For this application, context can be duck-typed as a Message
            await self._max_concurrency.acquire(ctx)  # type: ignore

        try:
            if self.cooldown_after_parsing:
                await self._parse_arguments(ctx)
                self._prepare_cooldowns(ctx)
            else:
                self._prepare_cooldowns(ctx)
                await self._parse_arguments(ctx)

            await self.call_before_hooks(ctx)
        except:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(ctx)  # type: ignore
            raise

    async def invoke(self, ctx: BaseContext) -> None:
        """Runs the command with checks.

        Parameters
        ----------
        ctx: :class:`.BaseContext`
            The context to pass into the command.
        """
        await self.prepare(ctx)

        # terminate the invoked_subcommand chain.
        # since we're in a regular command (and not a group) then
        # the invoked subcommand is None.
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None
        injected = hook_wrapped_callback(self, ctx, self.callback)
        await injected(*ctx.args, **ctx.kwargs)

    async def reinvoke(self, ctx: BaseContext, *, call_hooks: bool = False) -> None:
        """|coro|

        Calls the command again.

        This is similar to :meth:`Invokable.invoke` except that it bypasses
        checks, cooldowns, and error handlers.

        Parameters
        ----------
        ctx: BaseContext
            The context to invoke with.
        call_hooks: :class:`bool`
            Whether to call the before and after invoke hooks.
        """

        ctx.command = self
        await self._parse_arguments(ctx)

        if call_hooks:
            await self.call_before_hooks(ctx)

        ctx.invoked_subcommand = None
        try:
            await self.callback(*ctx.args, **ctx.kwargs)  # type: ignore
        except:
            ctx.command_failed = True
            raise
        finally:
            if call_hooks:
                await self.call_after_hooks(ctx)

    async def _dispatch_error(self, ctx: BaseContext, error: Exception) -> None:
        # since I don't want to copy paste code, subclassed Contexts
        # dispatch it to their corresponding events
        raise NotImplementedError

    async def dispatch_error(self, ctx: BaseContext, error: Exception) -> None:
        ctx.command_failed = True
        cog = self.cog

        if coro := getattr(self, "on_error", None):
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
            await self._dispatch_error(ctx, error)
