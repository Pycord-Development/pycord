"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

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
import inspect
from enum import Enum
from collections import OrderedDict

from .member import Member
from .abc import GuildChannel
from .role import Role
from .enums import SlashCommandOptionType

class SlashCommand:
    type = 1

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)

        self.__original_kwargs__ = kwargs.copy()
        return self
    def __init__(self, func, *args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine.')

        name = kwargs.get('name') or func.__name__
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')
        self.name = name

        description = kwargs.get('description') or inspect.cleandoc(func.__doc__)
        if description == None:
            description = "No description set"
        elif not isinstance(name, str):
            raise TypeError('Description of a command must be a string.')
        self.description = description

        options = OrderedDict(inspect.signature(func).parameters)
        options.pop(list(options)[0])
        for a, o in options:
            if o.name == None:
                o.name == a
        self.options = dict(options)


        self.callback = func
    
    def to_dict(self):
        return {
            "name":self.name,
            "description":self.description,
            "options":[o.to_dict() for o in self.options]
        }
    def __eq__(self, other):
        return (
            isinstance(other, SlashCommand)
            and other.name == self.name
            and other.description == self.description
        )

class Option:
    def __init__(self, type, /, **kwargs):
        self.name = kwargs.pop("name", None)
        self.description = kwargs.pop("description")
        if not isinstance(type, SlashCommandOptionType):
            type = SlashCommandOptionType.from_datatype(type)
        self.type = type
        self.required = kwargs.pop("required", False)
        self.choices = list(i for i in kwargs.pop("choices", list()))
    def to_dict(self):
        return {
            "name":self.name,
            "description":self.description,
            "type":int(self.type),
            "required":self.required,
            "choices":[c.to_dict() for c in self.choices]
        }
    
class OptionChoice:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value or name
    def to_dict(self):
        return {
            "name":self.name,
            "value":self.value
        }

class UserCommand:
    type = 2

class MessageCommand:
    type = 3
