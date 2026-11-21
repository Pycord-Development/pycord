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

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .components import Component


class EmbedFooter(TypedDict):
    text: str
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


class EmbedField(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


class EmbedVideo(TypedDict):
    url: NotRequired[str]
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]
    content_type: NotRequired[str]
    placeholder: NotRequired[str]
    placeholder_version: NotRequired[int]
    description: NotRequired[str]
    flags: NotRequired[int]


class EmbedImage(TypedDict):
    url: str
    proxy_url: NotRequired[str]
    height: NotRequired[int]
    width: NotRequired[int]
    content_type: NotRequired[str]
    placeholder: NotRequired[str]
    placeholder_version: NotRequired[int]
    description: NotRequired[str]
    flags: NotRequired[int]


class EmbedProvider(TypedDict):
    name: NotRequired[str]
    url: NotRequired[str]


class EmbedAuthor(TypedDict):
    name: str
    url: NotRequired[str]
    icon_url: NotRequired[str]
    proxy_icon_url: NotRequired[str]


EmbedType = Literal[
    "rich",
    "image",
    "video",
    "gifv",
    "article",
    "link",
    "auto_moderation_message",
    "poll_result",
    "components",
]


class Embed(TypedDict):
    title: NotRequired[str]
    type: NotRequired[EmbedType]
    description: NotRequired[str]
    url: NotRequired[str]
    timestamp: NotRequired[str]
    color: NotRequired[int]
    footer: NotRequired[EmbedFooter]
    image: NotRequired[EmbedImage]
    thumbnail: NotRequired[EmbedImage]
    video: NotRequired[EmbedVideo]
    provider: NotRequired[EmbedProvider]
    author: NotRequired[EmbedAuthor]
    fields: NotRequired[list[EmbedField]]
    components: NotRequired[list[Component]]
    flags: NotRequired[int]
