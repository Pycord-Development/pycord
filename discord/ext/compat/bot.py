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
from .core import CompatCommand, compat_command
from .context import CompatApplicationContext, CompatExtContext
from ..commands import Bot as ExtBot

__all__ = ("Bot",)

from ... import Interaction, Message


class Bot(ExtBot):
    async def get_application_context(self, interaction: Interaction, cls=None) -> CompatApplicationContext:
        cls = cls if cls is not None else CompatApplicationContext
        # Ignore the type hinting error here. CompatApplicationContext is a subclass of ApplicationContext, and since
        # we gave it cls, it will be used instead.
        return await super().get_application_context(interaction, cls=cls)  # type: ignore

    async def get_context(self, message: Message, cls=None) -> CompatExtContext:
        cls = cls if cls is not None else CompatExtContext
        # Ignore the type hinting error here. CompatExtContext is a subclass of Context, and since we gave it cls, it
        # will be used instead.
        return await super().get_context(message, cls=cls)  # type: ignore

    def add_compat_command(self, command: CompatCommand):
        command.add_to(self)

    def compat_command(self, **kwargs):
        def decorator(func) -> CompatCommand:
            result = compat_command(**kwargs)(func)
            self.add_compat_command(result)
            return result

        return decorator
