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

from typing import Any, Dict, List, Literal, Optional, Union
from re import findall

from ..enums import ChannelType, SlashCommandOptionType
# Needed for the gettype function
from ..channel import TextChannel, VoiceChannel, StageChannel, CategoryChannel
from ..member import Member
from ..threads import Thread
from ..user import User

__all__ = (
    "ThreadOption",
    "Option",
    "OptionChoice",
    "option",
)

channel_type_map = {
    "TextChannel": ChannelType.text,
    "VoiceChannel": ChannelType.voice,
    "StageChannel": ChannelType.stage_voice,
    "CategoryChannel": ChannelType.category,
    "Thread": ChannelType.public_thread,
}


class ThreadOption:
    def __init__(self, thread_type: Literal["public", "private", "news"]):
        type_map = {
            "public": ChannelType.public_thread,
            "private": ChannelType.private_thread,
            "news": ChannelType.news_thread,
        }
        self._type = type_map[thread_type]

    @property
    def __name__(self):
        return "ThreadOption"

class Option:
    def __init__(self, /, description: str = None, **kwargs) -> None:
        self.name: Optional[str] = kwargs.pop("name", None)
        self.description = description or "No description provided"
        self.converter = None

        #self._raw_type = input_type
        self.channel_types: List[ChannelType] = kwargs.pop(
            "channel_types", []
        )

        self.default = kwargs.pop("default", None)
        self.required: bool = (
            kwargs.pop("required", True) if self.default is None else False
        )
        self.choices: List[OptionChoice] = [
            o if isinstance(o, OptionChoice) else OptionChoice(o)
            for o in kwargs.pop("choices", list())
        ]
        
        self._raw_min_value = kwargs.pop("min_value", None)
        self._raw_max_value = kwargs.pop("max_value", None)

        self.autocomplete = kwargs.pop("autocomplete", None)

    def to_dict(self) -> Dict:
        as_dict = {
            "name": self.name,
            "description": self.description,
            "type": self.input_type.value,
            "required": self.required,
            "choices": [c.to_dict() for c in self.choices],
            "autocomplete": bool(self.autocomplete),
        }
        if self.channel_types:
            as_dict["channel_types"] = [t.value for t in self.channel_types]
        if self.min_value is not None:
            as_dict["min_value"] = self.min_value
        if self.max_value is not None:
            as_dict["max_value"] = self.max_value

        return as_dict

    def __repr__(self):
        return f"<discord.commands.{self.__class__.__name__} name={self.name}>"


class OptionChoice:
    def __init__(self, name: str, value: Optional[Union[str, int, float]] = None):
        self.name = name
        self.value = value if value is not None else name

    def to_dict(self) -> Dict[str, Union[str, int, float]]:
        return {"name": self.name, "value": self.value}


def option(name, type=None, **kwargs):
    """A decorator that can be used instead of typehinting Option"""

    def decorator(func):
        nonlocal type
        type = type or func.__annotations__.get(name, str)
        func.__annotations__[name] = Option(type, **kwargs)
        return func

    return decorator
