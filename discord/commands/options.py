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
    def __init__(self, input_type: Any, /, description: str = None, **kwargs) -> None:
        self.name: Optional[str] = kwargs.pop("name", None)
        self.description = description or "No description provided"
        self.converter = None
        self._raw_type = input_type
        self.channel_types: List[ChannelType] = kwargs.pop("channel_types", [])
        if not isinstance(input_type, SlashCommandOptionType):
            if hasattr(input_type, "convert"):
                self.converter = input_type
                input_type = SlashCommandOptionType.string
            else:
                try:
                    _type = SlashCommandOptionType.from_datatype(input_type)
                except TypeError as exc:
                    from ..ext.commands.converter import CONVERTER_MAPPING

                    if input_type not in CONVERTER_MAPPING:
                        raise exc
                    self.converter = CONVERTER_MAPPING[input_type]
                    input_type = SlashCommandOptionType.string
                else:
                    if _type == SlashCommandOptionType.channel:
                        if not isinstance(input_type, tuple):
                            input_type = (input_type,)
                        for i in input_type:
                            if i.__name__ == "GuildChannel":
                                continue
                            if isinstance(i, ThreadOption):
                                self.channel_types.append(i._type)
                                continue

                            channel_type = channel_type_map[i.__name__]
                            self.channel_types.append(channel_type)
                    input_type = _type
        self.input_type = input_type
        self.required: bool = kwargs.pop("required", True) if "default" not in kwargs else False
        self.default = kwargs.pop("default", None)
        self.choices: List[OptionChoice] = [
            o if isinstance(o, OptionChoice) else OptionChoice(o) for o in kwargs.pop("choices", list())
        ]

        if self.input_type == SlashCommandOptionType.integer:
            minmax_types = (int, type(None))
        elif self.input_type == SlashCommandOptionType.number:
            minmax_types = (int, float, type(None))
        else:
            minmax_types = (type(None),)
        minmax_typehint = Optional[Union[minmax_types]]  # type: ignore

        self.min_value: minmax_typehint = kwargs.pop("min_value", None)
        self.max_value: minmax_typehint = kwargs.pop("max_value", None)

        if not isinstance(self.min_value, minmax_types) and self.min_value is not None:
            raise TypeError(f'Expected {minmax_typehint} for min_value, got "{type(self.min_value).__name__}"')
        if not (isinstance(self.max_value, minmax_types) or self.min_value is None):
            raise TypeError(f'Expected {minmax_typehint} for max_value, got "{type(self.max_value).__name__}"')

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
