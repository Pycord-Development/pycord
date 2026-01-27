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

from typing_extensions import NotRequired, TypedDict

from .channel import ChannelType
from .emoji import PartialEmoji
from .snowflake import Snowflake

ComponentType = Literal[
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23
]
ButtonStyle = Literal[1, 2, 3, 4, 5, 6]
InputTextStyle = Literal[1, 2]
SeparatorSpacingSize = Literal[1, 2]
SelectDefaultValueType = Literal["channel", "role", "user"]


class BaseComponent(TypedDict):
    type: ComponentType
    id: NotRequired[int]


class ActionRow(BaseComponent):
    type: Literal[1]
    components: list[ButtonComponent | InputText | SelectMenu]


class ButtonComponent(BaseComponent):
    custom_id: NotRequired[str]
    url: NotRequired[str]
    disabled: NotRequired[bool]
    emoji: NotRequired[PartialEmoji]
    label: NotRequired[str]
    type: Literal[2]
    style: ButtonStyle
    sku_id: Snowflake


class InputText(BaseComponent):
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    placeholder: NotRequired[str]
    value: NotRequired[str]
    type: Literal[4]
    style: InputTextStyle
    custom_id: str
    label: NotRequired[str]


class SelectOption(TypedDict):
    description: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    label: str
    value: str
    default: bool


class SelectDefaultValue(TypedDict):
    id: Snowflake
    type: SelectDefaultValueType


class SelectMenu(BaseComponent):
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    disabled: NotRequired[bool]
    channel_types: NotRequired[list[ChannelType]]
    options: NotRequired[list[SelectOption]]
    type: Literal[3, 5, 6, 7, 8]
    custom_id: str
    required: NotRequired[bool]
    default_values: NotRequired[list[SelectDefaultValue]]


class TextDisplayComponent(BaseComponent):
    type: Literal[10]
    content: str


class SectionComponent(BaseComponent):
    type: Literal[9]
    components: list[TextDisplayComponent]
    accessory: NotRequired[ThumbnailComponent | ButtonComponent]


class UnfurledMediaItem(TypedDict):
    url: str
    proxy_url: str
    height: NotRequired[int | None]
    width: NotRequired[int | None]
    content_type: NotRequired[str]
    flags: NotRequired[int]
    attachment_id: NotRequired[Snowflake]


class ThumbnailComponent(BaseComponent):
    type: Literal[11]
    media: UnfurledMediaItem
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryItem(TypedDict):
    media: UnfurledMediaItem
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGalleryComponent(BaseComponent):
    type: Literal[12]
    items: list[MediaGalleryItem]


class FileComponent(BaseComponent):
    type: Literal[13]
    file: UnfurledMediaItem
    spoiler: NotRequired[bool]
    name: str
    size: int


class SeparatorComponent(BaseComponent):
    type: Literal[14]
    divider: NotRequired[bool]
    spacing: NotRequired[SeparatorSpacingSize]


class ContainerComponent(BaseComponent):
    type: Literal[17]
    accent_color: NotRequired[int]
    spoiler: NotRequired[bool]
    components: list[AllowedContainerComponents]


class LabelComponent(BaseComponent):
    type: Literal[18]
    label: str
    description: NotRequired[str]
    component: (
        SelectMenu
        | InputText
        | FileUploadComponent
        | RadioGroupComponent
        | CheckboxComponent
        | CheckboxGroupComponent
    )


class FileUploadComponent(BaseComponent):
    type: Literal[19]
    custom_id: str
    max_values: NotRequired[int]
    min_values: NotRequired[int]
    required: NotRequired[bool]


class RadioGroupOption(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class RadioGroupComponent(BaseComponent):
    type: Literal[21]
    custom_id: str
    required: NotRequired[bool]
    options: list[RadioGroupOption]


class CheckboxGroupOption(TypedDict):
    value: str
    label: str
    description: NotRequired[str]
    default: NotRequired[bool]


class CheckboxGroupComponent(BaseComponent):
    type: Literal[22]
    custom_id: str
    required: NotRequired[bool]
    options: list[CheckboxGroupOption]
    max_values: NotRequired[int]
    min_values: NotRequired[int]


class CheckboxComponent(BaseComponent):
    type: Literal[23]
    custom_id: str
    default: NotRequired[bool]


Component = Union[
    ActionRow, ButtonComponent, SelectMenu, InputText, FileUploadComponent
]


AllowedContainerComponents = Union[
    ActionRow,
    TextDisplayComponent,
    MediaGalleryComponent,
    FileComponent,
    SeparatorComponent,
    SectionComponent,
]
