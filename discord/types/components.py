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

from typing import Literal, Union

from .._typed_dict import NotRequired, TypedDict
from .channel import ChannelType
from .emoji import PartialEmoji

ComponentType = Literal[1, 2, 3, 4]
ButtonStyle = Literal[1, 2, 3, 4, 5]
InputTextStyle = Literal[1, 2]


class ActionRow(TypedDict):
    type: Literal[1]
    components: list[Component]


class ButtonComponent(TypedDict):
    custom_id: NotRequired[str]
    url: NotRequired[str]
    disabled: NotRequired[bool]
    emoji: NotRequired[PartialEmoji]
    label: NotRequired[str]
    type: Literal[2]
    style: ButtonStyle


class InputText(TypedDict):
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    placeholder: NotRequired[str]
    value: NotRequired[str]
    type: Literal[4]
    style: InputTextStyle
    custom_id: str
    label: str


class SelectOption(TypedDict):
    description: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    label: str
    value: str
    default: bool


class SelectMenu(TypedDict):
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    disabled: NotRequired[bool]
    channel_types: NotRequired[list[ChannelType]]
    options: NotRequired[list[SelectOption]]
    type: Literal[3, 5, 6, 7, 8]
    custom_id: str


Component = Union[ActionRow, ButtonComponent, SelectMenu, InputText]
