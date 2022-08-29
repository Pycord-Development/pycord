from __future__ import annotations

import asyncio
import datetime
import functools
from typing import (
    TYPE_CHECKING,
    TypeVar,
    Callable,
    Coroutine,
    Optional,
    Union,
    Generic,
    Any,
    Dict,
    List,
)

from .. import utils, abc
from ..errors import (
    ApplicationCommandError,
    CheckFailure,
    CommandError,
    CommandInvokeError,
    DisabledCommand,
)
from .cooldowns import BucketType, CooldownMapping, MaxConcurrency

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from ..bot import Bot, AutoShardedBot
    from ..user import User, ClientUser
    from ..member import Member
    from ..guild import Guild
    from ..message import Message
    from ..interactions import Interaction
    from ..abc import MessageableChannel
    from ..voice_client import VoiceProtocol
    from ..state import ConnectionState

    P = ParamSpec("P")
else:
    P = TypeVar("P")

BotT = TypeVar("BotT", bound="Union[Bot, AutoShardedBot]")
CogT = TypeVar("CogT", bound="Cog")
CallbackT = TypeVar("CallbackT")
ContextT = TypeVar("ContextT", bound="BaseContext")

T = TypeVar("T")
Coro = Coroutine[Any, Any, T]
MaybeCoro = Union[T, Coro[T]]

Check = Union[
    Callable[[CogT, ContextT], MaybeCoro[bool]],
    Callable[[ContextT], MaybeCoro[bool]],
]

Error = Union[
    Callable[[CogT, "BaseContext[Any]", CommandError], Coro[Any]],
    Callable[["BaseContext[Any]", CommandError], Coro[Any]],
]
ErrorT = TypeVar("ErrorT", bound="Error")

Hook = Union[
    Callable[[CogT, ContextT], Coro[Any]],
    Callable[[ContextT], Coro[Any]]
]
HookT = TypeVar("HookT", bound="Hook")


def unwrap_function(function: Callable[..., Any]) -> Callable[..., Any]:
    partial = functools.partial
    while True:
        if hasattr(function, "__wrapped__"):
            function = function.__wrapped__
        elif isinstance(function, partial):
            function = function.func
        else:
            return function


def wrap_callback(coro):
    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            ret = await coro(*args, **kwargs)
        except CommandError:
            raise
        except asyncio.CancelledError:
            return
        except Exception as exc:
            raise CommandInvokeError(exc) from exc
        return ret

    return wrapped


def hooked_wrapped_callback(command: Invokable, ctx: ContextT, coro: CallbackT):
    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
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

    return wrapped


class _BaseCommand:
    __slots__ = ()


class BaseContext(abc.Messageable, Generic[BotT]):
    def __init__(
        self,
        bot: Bot,
        command: Optional[Invokable],
        args: List[Any] = utils.MISSING,
        kwargs: Dict[str, Any] = utils.MISSING,
        *,
        invoked_with: Optional[str] = None,
        invoked_parents: List[str] = utils.MISSING,
        invoked_subcommand: Optional[Invokable] = None,
        subcommand_passed: Optional[str] = None,
        command_failed: bool = False

    ):
        self.bot: Bot = bot
        self.command: Optional[Invokable] = command
        self.args: List[Any] = args or []
        self.kwargs: Dict[str, Any] = kwargs or {}

        self.invoked_with: Optional[str] = invoked_with
        if not self.invoked_with and command:
            self.invoked_with = command.name

        self.invoked_parents: List[str] = invoked_parents or []
        if not self.invoked_parents and command:
            self.invoked_parents = [i.name for i in command.parents]

        # This will always be None for slash commands
        self.subcommand_passed: Optional[str] = subcommand_passed

        self.invoked_subcommand: Optional[Invokable] = invoked_subcommand
        self.command_failed: bool = command_failed

    async def invoke(self, command: Invokable[CogT, P, T], /, *args: P.args, **kwargs: P.kwargs) -> T:
        r"""|coro|

        Calls a command with the arguments given.

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
    def source(self) -> Union[Message, Interaction]:
        """Union[:class:`Message`, :class:`Interaction`]: Property to return a message or interaction
        depending on the context.
        """
        raise NotImplementedError()

    @property
    def _state(self) -> ConnectionState:
        return self.source._state

    @property
    def cog(self) -> Optional[Cog]:
        """Optional[:class:`.Cog`]: Returns the cog associated with this context's command.
        None if it does not exist."""

        if self.command is None:
            return None
        return self.command.cog

    @utils.cached_property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`.Guild`]: Returns the guild associated with this context's command.
        None if not available."""
        return self.source.guild

    @utils.cached_property
    def guild_id(self) -> Optional[int]:
        """:class:`int`: Returns the ID of the guild associated with this context's command."""
        return getattr(self.source, "guild_id", self.guild.id if self.guild else None)

    @utils.cached_property
    def channel(self) -> MessageableChannel:
        """Union[:class:`.abc.Messageable`]: Returns the channel associated with this context's command.
        Shorthand for :attr:`.Message.channel`.
        """
        return self.source.channel

    @utils.cached_property
    def channel_id(self) -> Optional[int]:
        """:class:`int`: Returns the ID of the channel associated with this context's command."""
        return getattr(self.source, "channel_id", self.channel.id if self.channel else None)

    @utils.cached_property
    def author(self) -> Union[User, Member]:
        """Union[:class:`.User`, :class:`.Member`]:
        Returns the author associated with this context's command. Shorthand for :attr:`.Message.author`
        """
        return self.source.author

    @property
    def user(self) -> Union[User, Member]:
        """Union[:class:`.User`, :class:`.Member`]: Alias for :attr:`BaseContext.author`."""
        return self.author

    @utils.cached_property
    def me(self) -> Union[Member, ClientUser]:
        """Union[:class:`.Member`, :class:`.ClientUser`]:
        Similar to :attr:`.Guild.me` except it may return the :class:`.ClientUser` in private message
        message contexts, or when :meth:`Intents.guilds` is absent.
        """
        # bot.user will never be None at this point.
        return self.guild.me if self.guild and self.guild.me else self.bot.user  # type: ignore

    @property
    def voice_client(self) -> Optional[VoiceProtocol]:
        """Optional[:class:`.VoiceProtocol`]: A shortcut to :attr:`.Guild.voice_client`\, if applicable."""
        return self.guild.voice_client if self.guild else None


class Invokable(Generic[CogT, P, T]):
    def __init__(self, func: CallbackT, **kwargs):
        self.module: Any = None
        self.cog: Optional[Cog]
        self.parent: Optional[Invokable] = parent if isinstance((parent := kwargs.get("parent")), _BaseCommand) else None
        self.callback: CallbackT = func

        self.name: str = str(kwargs.get("name", func.__name__))
        self.enabled: bool = kwargs.get("enabled", True)

        # checks
        if checks := getattr(func, "__commands_checks__", []):
            checks.reverse()

        checks += kwargs.get("checks", [])  # combine all the checks we find (kwargs or decorator)
        self.checks: List[Check] = checks

        # cooldowns
        cooldown = getattr(func, "__commands_cooldown__", kwargs.get("cooldown"))

        if cooldown is None:
            buckets = CooldownMapping(cooldown, BucketType.default)
        elif isinstance(cooldown, CooldownMapping):
            buckets = cooldown
        else:
            raise TypeError("Cooldown must be a an instance of CooldownMapping or None.")

        self._buckets: CooldownMapping = buckets

        # max concurrency
        self._max_concurrency: Optional[MaxConcurrency] = getattr(func, "__commands_max_concurrency__", kwargs.get("max_concurrency"))

        # hooks
        self._before_invoke: Optional[Hook] = None
        if hook := getattr(func, "__before_invoke__", None):
            self.before_invoke(hook)

        self._after_invoke: Optional[Hook] = None
        if hook := getattr(func, "__after_invoke__", None):
            self.after_invoke(hook)

        self.on_error: Optional[Error]

    @property
    def callback(self) -> CallbackT:
        return self._callback

    @callback.setter
    def callback(self, func: CallbackT) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback must be a coroutine.")

        self._callback = func
        unwrap = unwrap_function(func)
        self.module = unwrap.__module__

    @property
    def cooldown(self):
        return self._buckets._cooldown

    @property
    def parents(self) -> List[Invokable]:
        """List[:class:`Invokable`]: Retrieves the parents of this command.

        If the command has no parents then it returns an empty :class:`list`.

        For example in commands ``?a b c test``, the parents are ``[c, b, a]``.
        """
        entries = []
        command = self
        while command.parent is not None:  # type: ignore
            command = command.parent  # type: ignore
            entries.append(command)

        return entries

    @property
    def root_parent(self) -> Optional[Invokable]:
        """Optional[:class:`Invokable`]: Retrieves the root parent of this command.

        If the command has no parents then it returns ``None``.

        For example in commands ``?a b c test``, the root parent is ``a``.
        """
        if not self.parent:
            return None
        return self.parents[-1]

    @property
    def full_parent_name(self) -> Optional[str]:
        """:class:`str`: Retrieves the fully qualified parent command name.

        This the base command name required to execute it. For example,
        in ``/one two three`` the parent name would be ``one two``.
        """
        if self.parent:
            return self.parent.qualified_name

    @property
    def qualified_name(self) -> str:
        """:class:`str`: Retrieves the fully qualified command name.

        This is the full parent name with the command name as well.
        For example, in ``?one two three`` the qualified name would be
        ``one two three``.
        """
        if not self.parent:
            return self.name

        return f"{self.parent.qualified_name} {self.name}"

    @property
    def cog_name(self) -> Optional[str]:
        """Optional[:class:`str`]: The name of the cog this command belongs to, if any."""
        return type(self.cog).__cog_name__ if self.cog is not None else None

    def __str__(self) -> str:
        return self.qualified_name

    async def __call__(self, ctx: ContextT, *args: P.args, **kwargs: P.kwargs):
        """|coro|

        Calls the internal callback that the command holds.

        .. note::

            This bypasses all mechanisms -- including checks, converters,
            invoke hooks, cooldowns, etc. You must take care to pass
            the proper arguments and types to this function.

        """
        if self.cog is not None:
            return await self.callback(self.cog, ctx, *args, **kwargs)
        return await self.callback(ctx, *args, **kwargs)

    def update(self, **kwargs: Any) -> None:
        """Updates the :class:`Command` instance with updated attribute.
        
        Similar to creating a new instance except it updates the current.
        """
        self.__init__(self.callback, **dict(self.__original_kwargs__, **kwargs))

    def error(self, coro: ErrorT) -> ErrorT:
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

    def before_invoke(self, coro: HookT) -> HookT:
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

    def after_invoke(self, coro: HookT) -> HookT:
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

    async def can_run(self, ctx: ContextT) -> bool:
        """|coro|

        Checks if the command can be executed by checking all the predicates
        inside the :attr:`~Command.checks` attribute. This also checks whether the
        command is disabled.

        .. versionchanged:: 1.3
            Checks whether the command is disabled or not

        Parameters
        -----------
        ctx: :class:`.Context`
            The ctx of the command currently being invoked.

        Raises
        -------
        :class:`CommandError`
            Any command error that was raised during a check call will be propagated
            by this function.

        Returns
        --------
        :class:`bool`
            A boolean indicating if the command can be invoked.
        """
        if not self.enabled:
            raise DisabledCommand(f"{self.name} command is disabled")

        original = ctx.command
        ctx.command = self

        try:
            if not await ctx.bot.can_run(ctx):
                raise CheckFailure(f"The global check functions for command {self.qualified_name} failed.")

            # I personally don't think parent checks should be
            # run with the subcommand. It causes confusion, and
            # nerfs control for a bit of reduced redundancy
            # predicates = self.checks
            # if self.parent is not None:
            #     # parent checks should be run first
            #     predicates = self.parent.checks + predicates

            if (cog := self.cog) and (local_check := cog._get_overridden_method(cog.cog_check)):
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

    # depends on what to do with the application_command_error event

    # async def dispatch_error(self, ctx: ContextT, error: Exception) -> None:
    #     ctx.command_failed = True
    #     cog = self.cog

    #     if coro := getattr(self, "on_error", None):
    #         injected = wrap_callback(coro)
    #         if cog is not None:
    #             await injected(cog, ctx, error)
    #         else:
    #             await injected(ctx, error)

    #     try:
    #         if cog is not None:
    #             local = cog.__class__._get_overridden_method(cog.cog_command_error)
    #             if local is not None:
    #                 wrapped = wrap_callback(local)
    #                 await wrapped(ctx, error)
    #     finally:
    #         ctx.bot.dispatch("application_command_error", ctx, error)

    def add_check(self, func: Check) -> None:
        """Adds a check to the command.

        This is the non-decorator interface to :func:`.check`.

        Parameters
        -----------
        func: Callable
            The function that will be used as a check.
        """

        self.checks.append(func)

    def remove_check(self, func: Check) -> None:
        """Removes a check from the command.

        This function is idempotent and will not raise an exception
        if the function is not in the command's checks.

        Parameters
        -----------
        func: Callable
            The function to remove from the checks.
        """

        try:
            self.checks.remove(func)
        except ValueError:
            pass

    def _prepare_cooldowns(self, ctx: ContextT):
        if not self._buckets.valid:
            return

        current = datetime.datetime.now().timestamp()
        bucket = self._buckets.get_bucket(ctx, current)  # type: ignore # ctx instead of non-existent message

        if bucket:
            retry_after = bucket.update_rate_limit(current)

            if retry_after:
                raise CommandOnCooldown(bucket, retry_after, self._buckets.type)  # type: ignore

    def is_on_cooldown(self, ctx: ContextT) -> bool:
        """Checks whether the command is currently on cooldown.

        .. note::

            This uses the current time instead of the interaction time.

        Parameters
        -----------
        ctx: :class:`.ApplicationContext`
            The invocation context to use when checking the command's cooldown status.

        Returns
        --------
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
        -----------
        ctx: :class:`.ApplicationContext`
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
            current = utils.utcnow().timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    async def call_before_hooks(self, ctx: ContextT) -> None:
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

    async def call_after_hooks(self, ctx: ContextT) -> None:
        cog = self.cog
        if self._after_invoke is not None:
            instance = getattr(self._after_invoke, "__self__", cog)
            if instance:
                await self._after_invoke(instance, ctx)  # type: ignore
            else:
                await self._after_invoke(ctx)  # type: ignore

        # call the cog local hook if applicable:
        if cog is not None:
            # :troll:
            hook = cog.__class__._get_overridden_method(cog.cog_after_invoke)
            if hook is not None:
                await hook(ctx)

        hook = ctx.bot._after_invoke
        if hook is not None:
            await hook(ctx)

    async def _parse_arguments(self, ctx: ContextT) -> None:
        """Parses arguments and attaches them to the context class (Union[:class:`~ext.commands.Context`, :class:`.ApplicationContext`])"""
        raise NotImplementedError()

    async def prepare(self, ctx: ContextT) -> None:
        ctx.command = self

        if not await self.can_run(ctx):
            raise CheckFailure(f"The check functions for command {self.qualified_name} failed.")

        if self._max_concurrency is not None:
            # For this application, context can be duck-typed as a Message
            await self._max_concurrency.acquire(ctx)  # type: ignore

        try:
            self._prepare_cooldowns(ctx)
            await self._parse_arguments(ctx)

            await self.call_before_hooks(ctx)
        except:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(ctx)  # type: ignore
            raise

    async def invoke(self, ctx: ContextT) -> None:
        await self.prepare(ctx)

        # terminate the invoked_subcommand chain.
        # since we're in a regular command (and not a group) then
        # the invoked subcommand is None.
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None
        injected = hooked_wrapped_callback(self, ctx, self.callback)
        await injected(*ctx.args, **ctx.kwargs)

    async def reinvoke(self, ctx: ContextT, *, call_hooks: bool = False) -> None:
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

    def copy(self):
        """Creates a copy of this command.

        Returns
        --------
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

    def _update_copy(self, kwargs: Dict[str, Any]):
        if kwargs:
            kw = kwargs.copy()
            kw.update(self.__original_kwargs__)
            copy = self.__class__(self.callback, **kw)
            return self._ensure_assignment_on_copy(copy)
        else:
            return self.copy()
