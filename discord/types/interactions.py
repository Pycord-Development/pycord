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

from typing import TYPE_CHECKING, Dict, Literal, Union

from ..permissions import Permissions
from .channel import ChannelType
from .components import Component, ComponentType
from .embed import Embed
from .member import Member
from .message import Attachment
from .monetization import Entitlement
from .role import Role
from .snowflake import Snowflake
from .user import User

if TYPE_CHECKING:
    from .message import AllowedMentions, Message
    from ..interactions import InteractionChannel

from .._typed_dict import NotRequired, TypedDict

ApplicationCommandType = Literal[1, 2, 3]


class ApplicationCommand(TypedDict):
    id: Snowflake
    type: NotRequired[ApplicationCommandType]
    application_id: Snowflake
    guild_id: NotRequired[Snowflake]
    name: str
    name_localizations: NotRequired[dict[str, str] | None]
    description: str
    description_localizations: NotRequired[dict[str, str] | None]
    options: NotRequired[list[ApplicationCommandOption]]
    default_member_permissions: str | None
    dm_permission: NotRequired[bool]
    default_permission: NotRequired[bool | None]
    nsfw: NotRequired[bool]
    version: Snowflake


ApplicationCommandOptionType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class ApplicationCommandOption(TypedDict):
    type: ApplicationCommandOptionType
    name: str
    name_localizations: NotRequired[dict[str, str] | None]
    description: str
    description_localizations: NotRequired[dict[str, str] | None]
    required: bool
    options: NotRequired[list[ApplicationCommandOption]]
    choices: NotRequired[list[ApplicationCommandOptionChoice]]
    channel_types: NotRequired[list[ChannelType]]
    min_value: NotRequired[int | float]
    max_value: NotRequired[int | float]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    autocomplete: NotRequired[bool]


class ApplicationCommandOptionChoice(TypedDict):
    name: str
    name_localizations: NotRequired[dict[str, str] | None]
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


InteractionType = Literal[1, 2, 3, 4, 5]


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
    channel: NotRequired[InteractionChannel]
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
    entitlements: list[Entitlement]
    authorizing_integration_owners: AuthorizingIntegrationOwners
    context: InteractionContextType


class InteractionMetadata(TypedDict):
    id: Snowflake
    type: InteractionType
    user_id: Snowflake
    authorizing_integration_owners: AuthorizingIntegrationOwners
    original_response_message_id: NotRequired[Snowflake]
    interacted_message_id: NotRequired[Snowflake]
    triggering_interaction_metadata: NotRequired[InteractionMetadata]


class InteractionApplicationCommandCallbackData(TypedDict, total=False):
    tts: bool
    content: str
    embeds: list[Embed]
    allowed_mentions: AllowedMentions
    flags: int
    components: list[Component]


InteractionResponseType = Literal[1, 4, 5, 6, 7, 8, 9, 10]


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


InteractionContextType = Literal[0, 1, 2]
ApplicationIntegrationType = Literal[0, 1]
_StringApplicationIntegrationType = Literal["0", "1"]

AuthorizingIntegrationOwners = Dict[_StringApplicationIntegrationType, Snowflake]
