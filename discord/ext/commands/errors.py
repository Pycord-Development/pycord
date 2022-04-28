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

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Type, Union

from discord.errors import *

if TYPE_CHECKING:
    from inspect import Parameter

    from discord.abc import GuildChannel
    from discord.threads import Thread
    from discord.types.snowflake import Snowflake, SnowflakeList

    from .context import Context
    from .converter import Converter
    from .cooldowns import BucketType, Cooldown
    from .flags import Flag

    


__all__ = (
    "CommandError",
    "MissingRequiredArgument",
    "BadArgument",
    "PrivateMessageOnly",
    "NoPrivateMessage",
    "CheckFailure",
    "CheckAnyFailure",
    "CommandNotFound",
    "DisabledCommand",
    "CommandInvokeError",
    "TooManyArguments",
    "UserInputError",
    "CommandOnCooldown",
    "MaxConcurrencyReached",
    "NotOwner",
    "MessageNotFound",
    "ObjectNotFound",
    "MemberNotFound",
    "GuildNotFound",
    "UserNotFound",
    "ChannelNotFound",
    "ThreadNotFound",
    "ChannelNotReadable",
    "BadColourArgument",
    "BadColorArgument",
    "RoleNotFound",
    "BadInviteArgument",
    "EmojiNotFound",
    "GuildStickerNotFound",
    "PartialEmojiConversionFailure",
    "BadBoolArgument",
    "MissingRole",
    "BotMissingRole",
    "MissingAnyRole",
    "BotMissingAnyRole",
    "MissingPermissions",
    "BotMissingPermissions",
    "NSFWChannelRequired",
    "ConversionError",
    "BadUnionArgument",
    "BadLiteralArgument",
    "ArgumentParsingError",
    "UnexpectedQuoteError",
    "InvalidEndOfQuotedStringError",
    "ExpectedClosingQuoteError",
    "CommandRegistrationError",
    "FlagError",
    "BadFlagArgument",
    "MissingFlagArgument",
    "TooManyFlags",
    "MissingRequiredFlag",
    "NoMoreItems",
    "GatewayNotFound",
    "HTTPException",
    "Forbidden",
    "NotFound",
    "DiscordServerError",
    "InvalidData",
    "InvalidArgument",
    "LoginFailure",
    "ConnectionClosed",
    "PrivilegedIntentsRequired",
    "InteractionResponded",
    "ExtensionError",
    "ExtensionAlreadyLoaded",
    "ExtensionNotLoaded",
    "NoEntryPointError",
    "ExtensionFailed",
    "ExtensionNotFound",
    "ApplicationCommandError",
    "CheckFailure",
    "ApplicationCommandInvokeError",
)

class ApplicationCommandInvokeError(ApplicationCommandInvokeError):
    """Exception raised when the command being invoked raised an exception.
    This inherits from :exc:`ApplicationCommandError`
    Attributes
    -----------
    original: :exc:`Exception`
        The original exception that was raised. You can also get this via
        the ``__cause__`` attribute.
    """
    pass


class CheckFailure(CheckFailure):
    """Exception raised when the predicates in :attr:`.Command.checks` have failed.
    This inherits from :exc:`ApplicationCommandError`
    """

    pass


class ApplicationCommandError(ApplicationCommandError):
    r"""The base exception type for all application command related errors.
    This inherits from :exc:`DiscordException`.
    This exception and exceptions inherited from it are handled
    in a special way as they are caught and passed into a special event
    from :class:`.Bot`\, :func:`.on_command_error`.
    """
    pass


class ExtensionNotFound(ExtensionNotFound):
    """An exception raised when an extension is not found.
    This inherits from :exc:`ExtensionError`
    .. versionchanged:: 1.3
        Made the ``original`` attribute always None.
    Attributes
    -----------
    name: :class:`str`
        The extension that had the error.
    """
    pass


class ExtensionFailed(ExtensionFailed):
    """An exception raised when an extension failed to load during execution of the module or ``setup`` entry point.
    This inherits from :exc:`ExtensionError`
    Attributes
    -----------
    name: :class:`str`
        The extension that had the error.
    original: :exc:`Exception`
        The original exception that was raised. You can also get this via
        the ``__cause__`` attribute.
    """
    pass

class NoEntryPointError(NoEntryPointError):
    """An exception raised when an extension was not loaded.
    This inherits from :exc:`ExtensionError`
    """
    pass


class ExtensionNotLoaded(ExtensionError):
    """An exception raised when an extension was not loaded.
    This inherits from :exc:`ExtensionError`
    """
    pass
    


class ExtensionAlreadyLoaded(ExtensionAlreadyLoaded):
    """An exception raised when an extension has already been loaded.
    This inherits from :exc:`ExtensionError`
    """
    pass

class ExtensionError(ExtensionError):
    """Base exception for extension related errors.
    This inherits from :exc:`~discord.DiscordException`.
    Attributes
    ------------
    name: :class:`str`
        The extension that had an error.
    """
    pass



class InteractionResponded(InteractionResponded):
    """Exception that's raised when sending another interaction response using
    :class:`InteractionResponse` when one has already been done before.
    An interaction can only respond once.
    .. versionadded:: 2.0
    Attributes
    -----------
    interaction: :class:`Interaction`
        The interaction that's already been responded to.
    """
    pass


class PrivilegedIntentsRequired(PrivilegedIntentsRequired):
    """Exception that's raised when the gateway is requesting privileged intents
    but they're not ticked in the developer page yet.
    Go to https://discord.com/developers/applications/ and enable the intents
    that are required. Currently these are as follows:
    - :attr:`Intents.members`
    - :attr:`Intents.presences`
    - :attr:`Intents.message_content`
    Attributes
    -----------
    shard_id: Optional[:class:`int`]
        The shard ID that got closed if applicable.
    """
    pass


class ConnectionClosed(ConnectionClosed):
    """Exception that's raised when the gateway connection is
    closed for reasons that could not be handled internally.
    Attributes
    -----------
    code: :class:`int`
        The close code of the websocket.
    reason: :class:`str`
        The reason provided for the closure.
    shard_id: Optional[:class:`int`]
        The shard ID that got closed if applicable.
    """
    pass


class LoginFailure(LoginFailure):
    """Exception that's raised when the :meth:`Client.login` function
    fails to log you in from improper credentials or some other misc.
    failure.
    """

    pass


class InvalidArgument(InvalidArgument):
    """Exception that's raised when an argument to a function
    is invalid some way (e.g. wrong value or wrong type).
    This could be considered the analogous of ``ValueError`` and
    ``TypeError`` except inherited from :exc:`ClientException` and thus
    :exc:`DiscordException`.
    """

    pass


class InvalidData(InvalidData):
    """Exception that's raised when the library encounters unknown
    or invalid data from Discord.
    """

    pass


class DiscordServerError(DiscordServerError):
    """Exception that's raised for when a 500 range status code occurs.
    Subclass of :exc:`HTTPException`.
    .. versionadded:: 1.5
    """

    pass

class NotFound(NotFound):
    """Exception that's raised for when status code 404 occurs.
    Subclass of :exc:`HTTPException`
    """

    pass


class Forbidden(Forbidden):
    """Exception that's raised for when status code 403 occurs.
    Subclass of :exc:`HTTPException`
    """

    pass

class HTTPException(HTTPException):
    """Exception that's raised when an HTTP request operation fails.
    Attributes
    ------------
    response: :class:`aiohttp.ClientResponse`
        The response of the failed HTTP request. This is an
        instance of :class:`aiohttp.ClientResponse`. In some cases
        this could also be a :class:`requests.Response`.
    text: :class:`str`
        The text of the error. Could be an empty string.
    status: :class:`int`
        The status code of the HTTP request.
    code: :class:`int`
        The Discord specific error code for the failure.
    """
    pass


class ValidationError(ValidationError):
    """An Exception that is raised when there is a Validation Error."""

    pass

class GatewayNotFound(GatewayNotFound):
    """An exception that is raised when the gateway for Discord could not be found"""
    
    pass
class NoMoreItems(NoMoreItems):
    """Exception that is raised when an async iteration operation has no more items."""
    
    pass


class CommandError(DiscordException):
    r"""The base exception type for all command related errors.

    This inherits from :exc:`discord.DiscordException`.

    This exception and exceptions inherited from it are handled
    in a special way as they are caught and passed into a special event
    from :class:`.Bot`\, :func:`.on_command_error`.
    """

    def __init__(self, message: Optional[str] = None, *args: Any) -> None:
        if message is not None:
            # clean-up @everyone and @here mentions
            m = message.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
            super().__init__(m, *args)
        else:
            super().__init__(*args)


class ConversionError(CommandError):
    """Exception raised when a Converter class raises non-CommandError.

    This inherits from :exc:`CommandError`.

    Attributes
    ----------
    converter: :class:`discord.ext.commands.Converter`
        The converter that failed.
    original: :exc:`Exception`
        The original exception that was raised. You can also get this via
        the ``__cause__`` attribute.
    """

    def __init__(self, converter: Converter, original: Exception) -> None:
        self.converter: Converter = converter
        self.original: Exception = original


class UserInputError(CommandError):
    """The base exception type for errors that involve errors
    regarding user input.

    This inherits from :exc:`CommandError`.
    """

    pass


class CommandNotFound(CommandError):
    """Exception raised when a command is attempted to be invoked
    but no command under that name is found.

    This is not raised for invalid subcommands, rather just the
    initial main command that is attempted to be invoked.

    This inherits from :exc:`CommandError`.
    """

    pass


class MissingRequiredArgument(UserInputError):
    """Exception raised when parsing a command and a parameter
    that is required is not encountered.

    This inherits from :exc:`UserInputError`

    Attributes
    -----------
    param: :class:`inspect.Parameter`
        The argument that is missing.
    """

    def __init__(self, param: Parameter) -> None:
        self.param: Parameter = param
        super().__init__(f"{param.name} is a required argument that is missing.")


class TooManyArguments(UserInputError):
    """Exception raised when the command was passed too many arguments and its
    :attr:`.Command.ignore_extra` attribute was not set to ``True``.

    This inherits from :exc:`UserInputError`
    """

    pass


class BadArgument(UserInputError):
    """Exception raised when a parsing or conversion failure is encountered
    on an argument to pass into a command.

    This inherits from :exc:`UserInputError`
    """

    pass


class CheckFailure(CommandError):
    """Exception raised when the predicates in :attr:`.Command.checks` have failed.

    This inherits from :exc:`CommandError`
    """

    pass


class CheckAnyFailure(CheckFailure):
    """Exception raised when all predicates in :func:`check_any` fail.

    This inherits from :exc:`CheckFailure`.

    .. versionadded:: 1.3

    Attributes
    ------------
    errors: List[:class:`CheckFailure`]
        A list of errors that were caught during execution.
    checks: List[Callable[[:class:`Context`], :class:`bool`]]
        A list of check predicates that failed.
    """

    def __init__(self, checks: List[CheckFailure], errors: List[Callable[[Context], bool]]) -> None:
        self.checks: List[CheckFailure] = checks
        self.errors: List[Callable[[Context], bool]] = errors
        super().__init__("You do not have permission to run this command.")


class PrivateMessageOnly(CheckFailure):
    """Exception raised when an operation does not work outside of private
    message contexts.

    This inherits from :exc:`CheckFailure`
    """

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "This command can only be used in private messages.")


class NoPrivateMessage(CheckFailure):
    """Exception raised when an operation does not work in private message
    contexts.

    This inherits from :exc:`CheckFailure`
    """

    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "This command cannot be used in private messages.")


class NotOwner(CheckFailure):
    """Exception raised when the message author is not the owner of the bot.

    This inherits from :exc:`CheckFailure`
    """

    pass


class ObjectNotFound(BadArgument):
    """Exception raised when the argument provided did not match the format
    of an ID or a mention.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 2.0

    Attributes
    -----------
    argument: :class:`str`
        The argument supplied by the caller that was not matched
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f"{argument!r} does not follow a valid ID or mention format.")


class MemberNotFound(BadArgument):
    """Exception raised when the member provided was not found in the bot's
    cache.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The member supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Member "{argument}" not found.')


class GuildNotFound(BadArgument):
    """Exception raised when the guild provided was not found in the bot's cache.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.7

    Attributes
    -----------
    argument: :class:`str`
        The guild supplied by the called that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Guild "{argument}" not found.')


class UserNotFound(BadArgument):
    """Exception raised when the user provided was not found in the bot's
    cache.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The user supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'User "{argument}" not found.')


class MessageNotFound(BadArgument):
    """Exception raised when the message provided was not found in the channel.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The message supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Message "{argument}" not found.')


class ChannelNotReadable(BadArgument):
    """Exception raised when the bot does not have permission to read messages
    in the channel.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: Union[:class:`.abc.GuildChannel`, :class:`.Thread`]
        The channel supplied by the caller that was not readable
    """

    def __init__(self, argument: Union[GuildChannel, Thread]) -> None:
        self.argument: Union[GuildChannel, Thread] = argument
        super().__init__(f"Can't read messages in {argument.mention}.")


class ChannelNotFound(BadArgument):
    """Exception raised when the bot can not find the channel.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The channel supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Channel "{argument}" not found.')


class ThreadNotFound(BadArgument):
    """Exception raised when the bot can not find the thread.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 2.0

    Attributes
    -----------
    argument: :class:`str`
        The thread supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Thread "{argument}" not found.')


class BadColourArgument(BadArgument):
    """Exception raised when the colour is not valid.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The colour supplied by the caller that was not valid
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Colour "{argument}" is invalid.')


BadColorArgument = BadColourArgument


class RoleNotFound(BadArgument):
    """Exception raised when the bot can not find the role.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The role supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Role "{argument}" not found.')


class BadInviteArgument(BadArgument):
    """Exception raised when the invite is invalid or expired.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Invite "{argument}" is invalid or expired.')


class EmojiNotFound(BadArgument):
    """Exception raised when the bot can not find the emoji.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The emoji supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Emoji "{argument}" not found.')


class PartialEmojiConversionFailure(BadArgument):
    """Exception raised when the emoji provided does not match the correct
    format.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The emoji supplied by the caller that did not match the regex
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Couldn\'t convert "{argument}" to PartialEmoji.')


class GuildStickerNotFound(BadArgument):
    """Exception raised when the bot can not find the sticker.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 2.0

    Attributes
    -----------
    argument: :class:`str`
        The sticker supplied by the caller that was not found
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f'Sticker "{argument}" not found.')


class BadBoolArgument(BadArgument):
    """Exception raised when a boolean argument was not convertible.

    This inherits from :exc:`BadArgument`

    .. versionadded:: 1.5

    Attributes
    -----------
    argument: :class:`str`
        The boolean argument supplied by the caller that is not in the predefined list
    """

    def __init__(self, argument: str) -> None:
        self.argument: str = argument
        super().__init__(f"{argument} is not a recognised boolean option")


class DisabledCommand(CommandError):
    """Exception raised when the command being invoked is disabled.

    This inherits from :exc:`CommandError`
    """

    pass


class CommandInvokeError(CommandError):
    """Exception raised when the command being invoked raised an exception.

    This inherits from :exc:`CommandError`

    Attributes
    -----------
    original: :exc:`Exception`
        The original exception that was raised. You can also get this via
        the ``__cause__`` attribute.
    """

    def __init__(self, e: Exception) -> None:
        self.original: Exception = e
        super().__init__(f"Command raised an exception: {e.__class__.__name__}: {e}")


class CommandOnCooldown(CommandError):
    """Exception raised when the command being invoked is on cooldown.

    This inherits from :exc:`CommandError`

    Attributes
    -----------
    cooldown: :class:`.Cooldown`
        A class with attributes ``rate`` and ``per`` similar to the
        :func:`.cooldown` decorator.
    type: :class:`BucketType`
        The type associated with the cooldown.
    retry_after: :class:`float`
        The amount of seconds to wait before you can retry again.
    """

    def __init__(self, cooldown: Cooldown, retry_after: float, type: BucketType) -> None:
        self.cooldown: Cooldown = cooldown
        self.retry_after: float = retry_after
        self.type: BucketType = type
        super().__init__(f"You are on cooldown. Try again in {retry_after:.2f}s")


class MaxConcurrencyReached(CommandError):
    """Exception raised when the command being invoked has reached its maximum concurrency.

    This inherits from :exc:`CommandError`.

    Attributes
    ------------
    number: :class:`int`
        The maximum number of concurrent invokers allowed.
    per: :class:`.BucketType`
        The bucket type passed to the :func:`.max_concurrency` decorator.
    """

    def __init__(self, number: int, per: BucketType) -> None:
        self.number: int = number
        self.per: BucketType = per
        name = per.name
        suffix = f"per {name}" if per.name != "default" else "globally"
        plural = "%s times %s" if number > 1 else "%s time %s"
        fmt = plural % (number, suffix)
        super().__init__(f"Too many people are using this command. It can only be used {fmt} concurrently.")


class MissingRole(CheckFailure):
    """Exception raised when the command invoker lacks a role to run a command.

    This inherits from :exc:`CheckFailure`

    .. versionadded:: 1.1

    Attributes
    -----------
    missing_role: Union[:class:`str`, :class:`int`]
        The required role that is missing.
        This is the parameter passed to :func:`~.commands.has_role`.
    """

    def __init__(self, missing_role: Snowflake) -> None:
        self.missing_role: Snowflake = missing_role
        message = f"Role {missing_role!r} is required to run this command."
        super().__init__(message)


class BotMissingRole(CheckFailure):
    """Exception raised when the bot's member lacks a role to run a command.

    This inherits from :exc:`CheckFailure`

    .. versionadded:: 1.1

    Attributes
    -----------
    missing_role: Union[:class:`str`, :class:`int`]
        The required role that is missing.
        This is the parameter passed to :func:`~.commands.has_role`.
    """

    def __init__(self, missing_role: Snowflake) -> None:
        self.missing_role: Snowflake = missing_role
        message = f"Bot requires the role {missing_role!r} to run this command"
        super().__init__(message)


class MissingAnyRole(CheckFailure):
    """Exception raised when the command invoker lacks any of
    the roles specified to run a command.

    This inherits from :exc:`CheckFailure`

    .. versionadded:: 1.1

    Attributes
    -----------
    missing_roles: List[Union[:class:`str`, :class:`int`]]
        The roles that the invoker is missing.
        These are the parameters passed to :func:`~.commands.has_any_role`.
    """

    def __init__(self, missing_roles: SnowflakeList) -> None:
        self.missing_roles: SnowflakeList = missing_roles

        missing = [f"'{role}'" for role in missing_roles]

        if len(missing) > 2:
            fmt = f"{', '.join(missing[:-1])}, or {missing[-1]}"
        else:
            fmt = " or ".join(missing)

        message = f"You are missing at least one of the required roles: {fmt}"
        super().__init__(message)


class BotMissingAnyRole(CheckFailure):
    """Exception raised when the bot's member lacks any of
    the roles specified to run a command.

    This inherits from :exc:`CheckFailure`

    .. versionadded:: 1.1

    Attributes
    -----------
    missing_roles: List[Union[:class:`str`, :class:`int`]]
        The roles that the bot's member is missing.
        These are the parameters passed to :func:`~.commands.has_any_role`.

    """

    def __init__(self, missing_roles: SnowflakeList) -> None:
        self.missing_roles: SnowflakeList = missing_roles

        missing = [f"'{role}'" for role in missing_roles]

        if len(missing) > 2:
            fmt = f"{', '.join(missing[:-1])}, or {missing[-1]}"
        else:
            fmt = " or ".join(missing)

        message = f"Bot is missing at least one of the required roles: {fmt}"
        super().__init__(message)


class NSFWChannelRequired(CheckFailure):
    """Exception raised when a channel does not have the required NSFW setting.

    This inherits from :exc:`CheckFailure`.

    .. versionadded:: 1.1

    Parameters
    -----------
    channel: Union[:class:`.abc.GuildChannel`, :class:`.Thread`]
        The channel that does not have NSFW enabled.
    """

    def __init__(self, channel: Union[GuildChannel, Thread]) -> None:
        self.channel: Union[GuildChannel, Thread] = channel
        super().__init__(f"Channel '{channel}' needs to be NSFW for this command to work.")


class MissingPermissions(CheckFailure):
    """Exception raised when the command invoker lacks permissions to run a
    command.

    This inherits from :exc:`CheckFailure`

    Attributes
    -----------
    missing_permissions: List[:class:`str`]
        The required permissions that are missing.
    """

    def __init__(self, missing_permissions: List[str], *args: Any) -> None:
        self.missing_permissions: List[str] = missing_permissions

        missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in missing_permissions]

        if len(missing) > 2:
            fmt = f"{', '.join(missing[:-1])}, and {missing[-1]}"
        else:
            fmt = " and ".join(missing)
        message = f"You are missing {fmt} permission(s) to run this command."
        super().__init__(message, *args)


class BotMissingPermissions(CheckFailure):
    """Exception raised when the bot's member lacks permissions to run a
    command.

    This inherits from :exc:`CheckFailure`

    Attributes
    -----------
    missing_permissions: List[:class:`str`]
        The required permissions that are missing.
    """

    def __init__(self, missing_permissions: List[str], *args: Any) -> None:
        self.missing_permissions: List[str] = missing_permissions

        missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in missing_permissions]

        if len(missing) > 2:
            fmt = f"{', '.join(missing[:-1])}, and {missing[-1]}"
        else:
            fmt = " and ".join(missing)
        message = f"Bot requires {fmt} permission(s) to run this command."
        super().__init__(message, *args)


class BadUnionArgument(UserInputError):
    """Exception raised when a :data:`typing.Union` converter fails for all
    its associated types.

    This inherits from :exc:`UserInputError`

    Attributes
    -----------
    param: :class:`inspect.Parameter`
        The parameter that failed being converted.
    converters: Tuple[Type, ``...``]
        A tuple of converters attempted in conversion, in order of failure.
    errors: List[:class:`CommandError`]
        A list of errors that were caught from failing the conversion.
    """

    def __init__(self, param: Parameter, converters: Tuple[Type, ...], errors: List[CommandError]) -> None:
        self.param: Parameter = param
        self.converters: Tuple[Type, ...] = converters
        self.errors: List[CommandError] = errors

        def _get_name(x):
            try:
                return x.__name__
            except AttributeError:
                if hasattr(x, "__origin__"):
                    return repr(x)
                return x.__class__.__name__

        to_string = [_get_name(x) for x in converters]
        if len(to_string) > 2:
            fmt = f"{', '.join(to_string[:-1])}, or {to_string[-1]}"
        else:
            fmt = " or ".join(to_string)

        super().__init__(f'Could not convert "{param.name}" into {fmt}.')


class BadLiteralArgument(UserInputError):
    """Exception raised when a :data:`typing.Literal` converter fails for all
    its associated values.

    This inherits from :exc:`UserInputError`

    .. versionadded:: 2.0

    Attributes
    -----------
    param: :class:`inspect.Parameter`
        The parameter that failed being converted.
    literals: Tuple[Any, ``...``]
        A tuple of values compared against in conversion, in order of failure.
    errors: List[:class:`CommandError`]
        A list of errors that were caught from failing the conversion.
    """

    def __init__(self, param: Parameter, literals: Tuple[Any, ...], errors: List[CommandError]) -> None:
        self.param: Parameter = param
        self.literals: Tuple[Any, ...] = literals
        self.errors: List[CommandError] = errors

        to_string = [repr(l) for l in literals]
        if len(to_string) > 2:
            fmt = f"{', '.join(to_string[:-1])}, or {to_string[-1]}"
        else:
            fmt = " or ".join(to_string)

        super().__init__(f'Could not convert "{param.name}" into the literal {fmt}.')


class ArgumentParsingError(UserInputError):
    """An exception raised when the parser fails to parse a user's input.

    This inherits from :exc:`UserInputError`.

    There are child classes that implement more granular parsing errors for
    i18n purposes.
    """

    pass


class UnexpectedQuoteError(ArgumentParsingError):
    """An exception raised when the parser encounters a quote mark inside a non-quoted string.

    This inherits from :exc:`ArgumentParsingError`.

    Attributes
    ------------
    quote: :class:`str`
        The quote mark that was found inside the non-quoted string.
    """

    def __init__(self, quote: str) -> None:
        self.quote: str = quote
        super().__init__(f"Unexpected quote mark, {quote!r}, in non-quoted string")


class InvalidEndOfQuotedStringError(ArgumentParsingError):
    """An exception raised when a space is expected after the closing quote in a string
    but a different character is found.

    This inherits from :exc:`ArgumentParsingError`.

    Attributes
    -----------
    char: :class:`str`
        The character found instead of the expected string.
    """

    def __init__(self, char: str) -> None:
        self.char: str = char
        super().__init__(f"Expected space after closing quotation but received {char!r}")


class ExpectedClosingQuoteError(ArgumentParsingError):
    """An exception raised when a quote character is expected but not found.

    This inherits from :exc:`ArgumentParsingError`.

    Attributes
    -----------
    close_quote: :class:`str`
        The quote character expected.
    """

    def __init__(self, close_quote: str) -> None:
        self.close_quote: str = close_quote
        super().__init__(f"Expected closing {close_quote}.")


class CommandRegistrationError(ClientException):
    """An exception raised when the command can't be added
    because the name is already taken by a different command.

    This inherits from :exc:`discord.ClientException`

    .. versionadded:: 1.4

    Attributes
    ----------
    name: :class:`str`
        The command name that had the error.
    alias_conflict: :class:`bool`
        Whether the name that conflicts is an alias of the command we try to add.
    """

    def __init__(self, name: str, *, alias_conflict: bool = False) -> None:
        self.name: str = name
        self.alias_conflict: bool = alias_conflict
        type_ = "alias" if alias_conflict else "command"
        super().__init__(f"The {type_} {name} is already an existing command or alias.")


class FlagError(BadArgument):
    """The base exception type for all flag parsing related errors.

    This inherits from :exc:`BadArgument`.

    .. versionadded:: 2.0
    """

    pass


class TooManyFlags(FlagError):
    """An exception raised when a flag has received too many values.

    This inherits from :exc:`FlagError`.

    .. versionadded:: 2.0

    Attributes
    ------------
    flag: :class:`~discord.ext.commands.Flag`
        The flag that received too many values.
    values: List[:class:`str`]
        The values that were passed.
    """

    def __init__(self, flag: Flag, values: List[str]) -> None:
        self.flag: Flag = flag
        self.values: List[str] = values
        super().__init__(f"Too many flag values, expected {flag.max_args} but received {len(values)}.")


class BadFlagArgument(FlagError):
    """An exception raised when a flag failed to convert a value.

    This inherits from :exc:`FlagError`

    .. versionadded:: 2.0

    Attributes
    -----------
    flag: :class:`~discord.ext.commands.Flag`
        The flag that failed to convert.
    """

    def __init__(self, flag: Flag) -> None:
        self.flag: Flag = flag
        try:
            name = flag.annotation.__name__
        except AttributeError:
            name = flag.annotation.__class__.__name__

        super().__init__(f"Could not convert to {name!r} for flag {flag.name!r}")


class MissingRequiredFlag(FlagError):
    """An exception raised when a required flag was not given.

    This inherits from :exc:`FlagError`

    .. versionadded:: 2.0

    Attributes
    -----------
    flag: :class:`~discord.ext.commands.Flag`
        The required flag that was not found.
    """

    def __init__(self, flag: Flag) -> None:
        self.flag: Flag = flag
        super().__init__(f"Flag {flag.name!r} is required and missing")


class MissingFlagArgument(FlagError):
    """An exception raised when a flag did not get a value.

    This inherits from :exc:`FlagError`

    .. versionadded:: 2.0

    Attributes
    -----------
    flag: :class:`~discord.ext.commands.Flag`
        The flag that did not get a value.
    """

    def __init__(self, flag: Flag) -> None:
        self.flag: Flag = flag
        super().__init__(f"Flag {flag.name!r} does not have an argument")
