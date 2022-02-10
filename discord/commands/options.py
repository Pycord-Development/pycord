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

import inspect
from collections import OrderedDict
from types import MappingProxyType
from typing import Dict, get_type_hints, List, Literal, Optional, Union

from ..enums import ChannelType, SlashCommandOptionType


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
    def __init__(self, input_type = None, /, description: str = None, **kwargs) -> None:
        self.name: Optional[str] = kwargs.pop("name", None)
        self.description = description or "No description provided"
        self.converter = None

        self.channel_types: List[ChannelType] = kwargs.pop(
            "channel_types", []
        )

        if input_type is not None:
            option.input_type = input_type
            _type_checking_for_option(self)

        self.required: bool = (
            kwargs.pop("required", True) if "default" not in kwargs else False
        )
        self.default = kwargs.pop("default", None)
        self.choices: List[OptionChoice] = [
            o if isinstance(o, OptionChoice) else OptionChoice(o)
            for o in kwargs.pop("choices", list())
        ]
        
        self._raw_min_value = kwargs.pop("min_value", None)
        self._raw_max_value = kwargs.pop("max_value", None)

        if input_type is not None:
            _minmax_setting_for_option(self)

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

def _type_checking_for_option(option):
    option._raw_type = option.input_type
    input_type = option.input_type
    if not isinstance(option.input_type, SlashCommandOptionType):
        if hasattr(option.input_type, "convert"):
            option.converter = option.input_type
            input_type = SlashCommandOptionType.string
        else:
            try:
                _type = SlashCommandOptionType.from_datatype(option.input_type)
            except TypeError as exc:
                from ..ext.commands.converter import CONVERTER_MAPPING

                if option.input_type in CONVERTER_MAPPING:
                    option.converter = CONVERTER_MAPPING[option.input_type]
                    input_type = SlashCommandOptionType.string
                else:
                    raise exc
            else:
                if _type == SlashCommandOptionType.channel:
                    if not isinstance(option.input_type, tuple):
                        input_type = (option.input_type,)
                    for i in input_type:
                        if i.__name__ == "GuildChannel":
                            continue
                        if isinstance(i, ThreadOption):
                            option.channel_types.append(i._type)
                            continue

                        channel_type = channel_type_map[i.__name__]
                        option.channel_types.append(channel_type)
                input_type = _type
    option.input_type = input_type

    return option

def _minmax_setting_for_option(option):
    if option.input_type == SlashCommandOptionType.integer:
        minmax_types = (int, type(None))
    elif option.input_type == SlashCommandOptionType.number:
        minmax_types = (int, float, type(None))
    else:
        minmax_types = (type(None),)
    minmax_typehint = Optional[Union[minmax_types]]  # type: ignore

    option.min_value: minmax_typehint = option._raw_min_value
    option.max_value: minmax_typehint = option._raw_max_value

    if (
        not isinstance(option.min_value, minmax_types)
        and option.min_value is not None
    ):
        raise TypeError(
            f'Expected {minmax_typehint} for min_value, got "{type(option.min_value).__name__}"'
        )
    if not (isinstance(option.max_value, minmax_types) or option.min_value is None):
        raise TypeError(
            f'Expected {minmax_typehint} for max_value, got "{type(option.max_value).__name__}"'
        )

    return option

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
        # first we check if the provided name is actually in the parameters
        parameters = OrderedDict(inspect.signature(func).parameters)

        # this means that there is a parameter with the same name
        if parameters.get(name):
            type_hints = get_type_hints(func)
            type = type or type_hints.get(name, str)

            opt = Option(**kwargs)
            opt.name = name
            opt._parameter_name = name
            opt.input_type = type
            
            func.__annotations__[name] = opt
        else:
            raise RuntimeError(
                f"Unknown parameter with name {name} from option decorator"
            )

        return func

    return decorator
