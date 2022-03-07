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
from typing import Union

from discord.commands import SlashCommand
from ..commands import Bot as ExtBot, AutoShardedBot as ExtAutoShardedBot, Command

__all__ = ("CompatCommand", "compat_command", "CompatExtCommand", "CompatSlashCommand")


class CompatSlashCommand(SlashCommand):
    ...


class CompatExtCommand(Command):
    ...


class CompatCommand:
    def __init__(self, callback, **kwargs):
        self.callback = callback
        self.kwargs = kwargs

    def get_ext_command(self):
        command = CompatExtCommand(self.callback, **self.kwargs)
        return command

    def get_application_command(self):
        command = CompatSlashCommand(self.callback, **self.kwargs)
        return command

    def add_to(self, bot: Union[ExtBot, ExtAutoShardedBot]) -> None:
        bot.add_command(self.get_ext_command())
        bot.add_application_command(self.get_application_command())


def compat_command(**kwargs):
    def decorator(callback):
        return CompatCommand(callback, **kwargs)

    return decorator
