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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Union, Any

from discord.commands import ApplicationContext
from discord.interactions import Interaction
from discord.message import Message
from discord.webhook import WebhookMessage
from ..commands import Context

__all__ = ("CompatContext", "CompatExtContext", "CompatApplicationContext")


class CompatContext(ABC):
    """
    The base context class for compatibility commands. This class is an :class:`ABC` (abstract base class), which is
    subclassed by :class:`CompatExtContext` and :class:`CompatApplicationContext`. The methods in this class are meant
    to give parity between the two contexts, while still allowing for all of their functionality.

    When this is passed to a command, it will either be passed as :class:`CompatExtContext`, or
    :class:`CompatApplicationContext`. Since they are two separate classes, it is quite simple to use :meth:`isinstance`
    to make different functionality for each context. For example, if you want to respond to a command with the command
    type that it was invoked with, you can do the following:

    .. code-block:: python3

        @bot.compat_command()
        async def example(ctx: CompatContext):
            if isinstance(ctx, CompatExtContext):
                command_type = "Traditional (prefix-based) command"
            elif isinstance(ctx, CompatApplicationContext):
                command_type = "Application command"
            await ctx.send(f"This command was invoked with a(n) {command_type}.")

    .. versionadded:: 2.0
    """

    @abstractmethod
    async def _respond(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        pass

    @abstractmethod
    async def _defer(self, *args, **kwargs) -> None:
        pass

    async def respond(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        """|coro|

        Responds to the command with the respective response type to the current context. In :class:`CompatExtContext`,
        this will be :meth:`~.ExtContext.reply` while in :class:`CompatApplicationContext`, this will be
        :meth:`~.ApplicationContext.respond`.
        """
        return await self._respond(*args, **kwargs)

    async def reply(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        """|coro|

        Alias for :meth:`~.CompatContext.respond`.
        """
        return await self.respond(*args, **kwargs)

    async def followup(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        """|coro|

        Alias for :meth:`~.CompatContext.respond`.
        """
        return await self.respond(*args, **kwargs)

    async def defer(self, *args, **kwargs) -> None:
        """|coro|

        Defers the command with the respective approach to the current context. In :class:`CompatExtContext`, this will
        be :meth:`~.ExtContext.trigger_typing` while in :class:`CompatApplicationContext`, this will be
        :meth:`~.ApplicationContext.defer`.

        .. note::
            There is no ``trigger_typing`` alias for this method. ``trigger_typing`` will always provide the same
            functionality across contexts.
        """
        return await self._defer(*args, **kwargs)

    def _get_super(self, attr: str) -> Optional[Any]:
        return getattr(super(), attr)


class CompatApplicationContext(CompatContext, ApplicationContext):
    """
    The application context class for compatibility commands. This class is a subclass of :class:`CompatContext` and
    :class:`ApplicationContext`. This class is meant to be used with :class:`CompatCommand`.

    .. versionadded:: 2.0
    """

    async def _respond(self, *args, **kwargs) -> Union[Interaction, WebhookMessage]:
        return await self._get_super("respond")(*args, **kwargs)

    async def _defer(self, *args, **kwargs) -> None:
        return await self._get_super("defer")(*args, **kwargs)


class CompatExtContext(CompatContext, Context):
    """
    The ext.commands context class for compatibility commands. This class is a subclass of :class:`CompatContext` and
    :class:`Context`. This class is meant to be used with :class:`CompatCommand`.

    .. versionadded:: 2.0
    """

    async def _respond(self, *args, **kwargs) -> Message:
        return await self._get_super("reply")(*args, **kwargs)

    async def _defer(self, *args, **kwargs) -> None:
        return await self._get_super("typing")(*args, **kwargs)


if TYPE_CHECKING:
    # This is a workaround for mypy not being able to resolve the type of CompatCommand.
    class CompatContext(ApplicationContext, Context):
        ...
