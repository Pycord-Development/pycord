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

from typing import TYPE_CHECKING, Literal, Union

from ..permissions import Permissions
from .channel import ChannelType
from .components import Component, ComponentType
from .embed import Embed
from .member import Member
from .message import Attachment
from .role import Role
from .snowflake import Snowflake
from .user import User

if TYPE_CHECKING:
    from .message import AllowedMentions, Message

from .._typed_dict import NotRequired, TypedDict

ApplicationCommandType = Literal[1, 2, 3]


class ApplicationCommand(TypedDict):
    options: NotRequired[list[ApplicationCommandOption]]
    type: NotRequired[ApplicationCommandType]
    name_localized: NotRequired[str]
    name_localizations: NotRequired[dict[str, str]]
    description_localized: NotRequired[str]
    description_localizations: NotRequired[dict[str, str]]
    id: Snowflake
    application_id: Snowflake
    name: str
    description: str


ApplicationCommandOptionType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class ApplicationCommandOption(TypedDict):
    choices: NotRequired[list[ApplicationCommandOptionChoice]]
    options: NotRequired[list[ApplicationCommandOption]]
    name_localizations: NotRequired[dict[str, str]]
    description_localizations: NotRequired[dict[str, str]]
    type: ApplicationCommandOptionType
    name: str
    description: str
    required: bool


class ApplicationCommandOptionChoice(TypedDict):
    name_localizations: NotRequired[dict[str, str]]
    name: str
    value: str | int


ApplicationCommandPermissionType = Literal[1, 2, 3]


class ApplicationCommandPermissions(TypedDict):
    id: Snowflake
    type: ApplicationCommandPermissionType
    permission: bool


class BaseGuildApplicationCommandPermissions(TypedDict):
    permissions: list[ApplicationCommandPermissions]


class PartialGuildApplicationCommandPermissions(BaseGuildApplicationCommandPermissions):
    id: Snowflake


class GuildApplicationCommandPermissions(PartialGuildApplicationCommandPermissions):
    application_id: Snowflake
    guild_id: Snowflake


InteractionType = Literal[1, 2, 3]


class _ApplicationCommandInteractionDataOption(TypedDict):
    name: str


class _ApplicationCommandInteractionDataOptionSubcommand(
    _ApplicationCommandInteractionDataOption
):
    type: Literal[1, 2]
    options: list[ApplicationCommandInteractionDataOption]


class _ApplicationCommandInteractionDataOptionString(
    _ApplicationCommandInteractionDataOption
):
    type: Literal[3]
    value: str


class _ApplicationCommandInteractionDataOptionInteger(
    _ApplicationCommandInteractionDataOption
):
    type: Literal[4]
    value: int


class _ApplicationCommandInteractionDataOptionBoolean(
    _ApplicationCommandInteractionDataOption
):
    type: Literal[5]
    value: bool


class _ApplicationCommandInteractionDataOptionSnowflake(
    _ApplicationCommandInteractionDataOption
):
    type: Literal[6, 7, 8, 9, 11]
    value: Snowflake


class _ApplicationCommandInteractionDataOptionNumber(
    _ApplicationCommandInteractionDataOption
):
    type: Literal[10]
    value: float


ApplicationCommandInteractionDataOption = Union[
    _ApplicationCommandInteractionDataOptionString,
    _ApplicationCommandInteractionDataOptionInteger,
    _ApplicationCommandInteractionDataOptionSubcommand,
    _ApplicationCommandInteractionDataOptionBoolean,
    _ApplicationCommandInteractionDataOptionSnowflake,
    _ApplicationCommandInteractionDataOptionNumber,
]


class ApplicationCommandResolvedPartialChannel(TypedDict):
    id: Snowflake
    type: ChannelType
    permissions: str
    name: str


class ApplicationCommandInteractionDataResolved(TypedDict, total=False):
    users: dict[Snowflake, User]
    members: dict[Snowflake, Member]
    roles: dict[Snowflake, Role]
    channels: dict[Snowflake, ApplicationCommandResolvedPartialChannel]
    attachments: dict[Snowflake, Attachment]


class ApplicationCommandInteractionData(TypedDict):
    options: NotRequired[list[ApplicationCommandInteractionDataOption]]
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]
    target_id: NotRequired[Snowflake]
    type: NotRequired[ApplicationCommandType]
    id: Snowflake
    name: str


class ComponentInteractionData(TypedDict):
    values: NotRequired[list[str]]
    custom_id: str
    component_type: ComponentType


InteractionData = Union[ApplicationCommandInteractionData, ComponentInteractionData]


class Interaction(TypedDict):
    data: NotRequired[InteractionData]
    guild_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    member: NotRequired[Member]
    user: NotRequired[User]
    message: NotRequired[Message]
    locale: NotRequired[str]
    guild_locale: NotRequired[str]
    app_permissions: NotRequired[Permissions]
    id: Snowflake
    application_id: Snowflake
    type: InteractionType
    token: str
    version: int


class InteractionApplicationCommandCallbackData(TypedDict, total=False):
    tts: bool
    content: str
    embeds: list[Embed]
    allowed_mentions: AllowedMentions
    flags: int
    components: list[Component]


InteractionResponseType = Literal[1, 4, 5, 6, 7]


class InteractionResponse(TypedDict):
    data: NotRequired[InteractionApplicationCommandCallbackData]
    type: InteractionResponseType


class MessageInteraction(TypedDict):
    id: Snowflake
    type: InteractionType
    name: str
    user: User


class EditApplicationCommand(TypedDict):
    description: NotRequired[str]
    options: NotRequired[list[ApplicationCommandOption] | None]
    type: NotRequired[ApplicationCommandType]
    name: str
    default_permission: bool
