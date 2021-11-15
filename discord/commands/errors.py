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

from ..errors import DiscordException
from typing import TYPE_CHECKING, Optional, Any

__all__ = (
    "ApplicationCommandError",
    "CheckFailure",
    "ApplicationCommandInvokeError",
    "CommandError",
    "CommandOnCooldown",
    "MaxConcurrencyReached",
)

class ApplicationCommandError(DiscordException):
    r"""The base exception type for all application command related errors.

    This inherits from :exc:`discord.DiscordException`.

    This exception and exceptions inherited from it are handled
    in a special way as they are caught and passed into a special event
    from :class:`.Bot`\, :func:`.on_command_error`.
    """
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
            m = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
            super().__init__(m, *args)
        else:
            super().__init__(*args)

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
    def __init__(self, cooldown, retry_after: float, type) -> None:
        self.cooldown = cooldown
        self.retry_after: float = retry_after
        self.type = type
        super().__init__(f'You are on cooldown. Try again in {retry_after:.2f}s')


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

    def __init__(self, number: int, per) -> None:
        self.number: int = number
        self.per = per
        name = per.name
        suffix = 'per %s' % name if per.name != 'default' else 'globally'
        plural = '%s times %s' if number > 1 else '%s time %s'
        fmt = plural % (number, suffix)
        super().__init__(f'Too many people are using this command. It can only be used {fmt} concurrently.')


class CheckFailure(ApplicationCommandError):
    """Exception raised when the predicates in :attr:`.Command.checks` have failed.

    This inherits from :exc:`ApplicationCommandError`
    """
    pass

class ApplicationCommandInvokeError(ApplicationCommandError):
    """Exception raised when the command being invoked raised an exception.

    This inherits from :exc:`ApplicationCommandError`

    Attributes
    -----------
    original: :exc:`Exception`
        The original exception that was raised. You can also get this via
        the ``__cause__`` attribute.
    """
    def __init__(self, e: Exception) -> None:
        self.original: Exception = e
        super().__init__(f'Application Command raised an exception: {e.__class__.__name__}: {e}')
