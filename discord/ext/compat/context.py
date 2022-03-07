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

from discord import ApplicationContext, Interaction, WebhookMessage, Message
from discord.ext.commands import Context


__all__ = ("CompatContext", "CompatExtContext", "CompatApplicationContext")


class CompatContext(ABC):
    @abstractmethod
    async def _respond(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        pass

    @abstractmethod
    async def _defer(self, *args, **kwargs) -> None:
        pass

    async def respond(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        return await self._respond(*args, **kwargs)

    async def reply(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        return await self.respond(*args, **kwargs)

    async def followup(self, *args, **kwargs) -> Union[Union[Interaction, WebhookMessage], Message]:
        return await self.respond(*args, **kwargs)

    async def defer(self, *args, **kwargs) -> None:
        return await self._defer(*args, **kwargs)

    def _get_super(self, attr: str) -> Optional[Any]:
        return getattr(super(), attr)


class CompatApplicationContext(CompatContext, ApplicationContext):
    async def _respond(self, *args, **kwargs) -> Union[Interaction, WebhookMessage]:
        return await self._get_super("respond")(*args, **kwargs)

    async def _defer(self, *args, **kwargs) -> None:
        return await self._get_super("defer")(*args, **kwargs)


class CompatExtContext(CompatContext, Context):
    async def _respond(self, *args, **kwargs) -> Message:
        return await self._get_super("reply")(*args, **kwargs)

    async def _defer(self, *args, **kwargs) -> None:
        return await self._get_super("typing")(*args, **kwargs)


if TYPE_CHECKING:
    class CompatContext(ApplicationContext, Context):
        ...
