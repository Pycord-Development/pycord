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

from typing import TYPE_CHECKING, Literal, TypedDict

from .snowflake import Snowflake

if TYPE_CHECKING:
    from .appinfo import ApplicationIntegrationType
    from .channel import ChannelType, PartialChannel
    from .components import Component, ComponentType
    from .embed import Embed
    from .guild import Guild
    from .member import Member, PartialMember
    from .message import Attachment
    from .monetization import Entitlement
    from .poll import Poll
    from .role import Role
    from .user import User
    from ..permissions import Permissions
    from .message import AllowedMentions, Message

from typing_extensions import NotRequired

ApplicationCommandType = Literal[
    1,  # CHAT_INPUT
    2,  # USER
    3,  # MESSAGE
    4,  # PRIMARY_ENTRY_POINT
]

InteractionContextType = Literal[
    0,  # GUILD
    1,  # BOT_DM
    2,  # PRIVATE_CHANNEL
]

CommandHandlerType = Literal[
    1,  # APP_HANDLER
    2,  # DISCORD_LAUNCH_ACTIVITY
]


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
    default_permission: NotRequired[bool | None]  # Soon to be deprecated
    nsfw: NotRequired[bool]
    integration_types: NotRequired[list[ApplicationIntegrationType]]
    contexts: NotRequired[list[InteractionContextType]]
    version: Snowflake
    handler: NotRequired[CommandHandlerType]


ApplicationCommandOptionType = Literal[
    1,  # SUB_COMMAND
    2,  # SUB_COMMAND_GROUP
    3,  # STRING
    4,  # INTEGER
    5,  # BOOLEAN
    6,  # USER
    7,  # CHANNEL
    8,  # ROLE
    9,  # MENTIONABLE
    10,  # NUMBER, "any double between -2^53 and 2^53"
    11,  # ATTACHMENT
]


class ApplicationCommandOption(TypedDict):
    type: ApplicationCommandOptionType
    name: str
    name_localizations: NotRequired[dict[str, str] | None]
    description: str
    description_localizations: NotRequired[dict[str, str] | None]
    required: NotRequired[bool]
    choices: NotRequired[list[ApplicationCommandOptionChoice]]
    options: NotRequired[list[ApplicationCommandOption]]
    channel_types: NotRequired[list[ChannelType]]
    min_value: NotRequired[int | float]
    max_value: NotRequired[int | float]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    autocomplete: NotRequired[bool]
    file_types: NotRequired[list[str]]


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


ApplicationCommandInteractionDataOption = (
    _ApplicationCommandInteractionDataOptionString
    | _ApplicationCommandInteractionDataOptionInteger
    | _ApplicationCommandInteractionDataOptionSubcommand
    | _ApplicationCommandInteractionDataOptionBoolean
    | _ApplicationCommandInteractionDataOptionSnowflake
    | _ApplicationCommandInteractionDataOptionNumber
)


class ApplicationCommandResolvedPartialChannel(TypedDict):
    id: Snowflake
    type: ChannelType
    permissions: str
    name: str


class ApplicationCommandInteractionDataResolved(TypedDict):
    users: NotRequired[dict[Snowflake, User]]
    members: NotRequired[dict[Snowflake, PartialMember]]
    roles: NotRequired[dict[Snowflake, Role]]
    channels: NotRequired[dict[Snowflake, ApplicationCommandResolvedPartialChannel]]
    attachments: NotRequired[dict[Snowflake, Attachment]]


class ApplicationCommandInteractionData(TypedDict):
    options: NotRequired[list[ApplicationCommandInteractionDataOption]]
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]
    target_id: NotRequired[Snowflake]
    type: NotRequired[ApplicationCommandType]
    id: Snowflake
    name: str


class MessageComponentInteractionData(TypedDict):
    values: NotRequired[list[str]]
    custom_id: str
    component_type: ComponentType


class ModalSubmitInteractionData(TypedDict):
    custom_id: str
    components: list[list[ComponentInteractionResponse]]
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]


class StringSelectInteractionResponse(TypedDict):
    """In message interaction responses component_type will be returned and in modal interaction responses type will be returned."""

    type: NotRequired[Literal[3]]
    component_type: NotRequired[Literal[3]]
    id: int
    custom_id: str
    values: list[str]


class TextInputInteractionResponse(TypedDict):
    type: Literal[4]
    id: int
    custom_id: str
    value: str


class UserSelectInteractionResponse(TypedDict):
    """In message interaction responses component_type will be returned and in modal interaction responses type will be returned."""

    type: NotRequired[Literal[5]]
    component_type: NotRequired[Literal[5]]
    id: int
    custom_id: str
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]
    values: list[Snowflake]


class RoleSelectInteractionResponse(TypedDict):
    """In message interaction responses component_type will be returned and in modal interaction responses type will be returned."""

    type: NotRequired[Literal[6]]
    component_type: NotRequired[Literal[6]]
    id: int
    custom_id: str
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]
    values: list[Snowflake]


class MentionableSelectInteractionResponse(TypedDict):
    """In message interaction responses component_type will be returned and in modal interaction responses type will be returned."""

    type: NotRequired[Literal[7]]
    component_type: NotRequired[Literal[7]]
    id: int
    custom_id: str
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]
    values: list[Snowflake]


class ChannelSelectInteractionResponse(TypedDict):
    """In message interaction responses component_type will be returned and in modal interaction responses type will be returned."""

    type: NotRequired[Literal[8]]
    component_type: NotRequired[Literal[8]]
    id: int
    custom_id: str
    resolved: NotRequired[ApplicationCommandInteractionDataResolved]
    values: list[Snowflake]


class FileUploadInteractionResponse(TypedDict):
    type: NotRequired[Literal[19]]
    id: int
    custom_id: str
    values: list[Snowflake]


class RadioGroupInteractionResponse(TypedDict):
    type: Literal[21]
    id: int
    custom_id: str
    value: str | None


class CheckBoxGroupInteractionResponse(TypedDict):
    type: Literal[22]
    id: int
    custom_id: str
    values: list[str]


class CheckBoxInteractionResponse(TypedDict):
    type: Literal[23]
    id: int
    custom_id: str
    value: bool


ComponentInteractionResponse = (
    StringSelectInteractionResponse
    | TextInputInteractionResponse
    | UserSelectInteractionResponse
    | RoleSelectInteractionResponse
    | MentionableSelectInteractionResponse
    | ChannelSelectInteractionResponse
    | FileUploadInteractionResponse
    | RadioGroupInteractionResponse
    | CheckBoxGroupInteractionResponse
    | CheckBoxInteractionResponse
)

InteractionData = ApplicationCommandInteractionData | MessageComponentInteractionData

InteractionType = Literal[
    1,  # PING
    2,  # APPLICATION_COMMAND
    3,  # MESSAGE_COMPONENT
    4,  # APPLICATION_COMMAND_AUTOCOMPLETE
    5,  # MODAL_SUBMIT
]


class Interaction(TypedDict):
    id: Snowflake
    application_id: Snowflake
    type: InteractionType
    data: NotRequired[InteractionData]
    guild: NotRequired[Guild]
    guild_id: NotRequired[Snowflake]
    channel_id: NotRequired[Snowflake]
    channel: NotRequired[PartialChannel]
    member: NotRequired[Member]
    user: NotRequired[User]
    token: str
    version: int
    message: NotRequired[Message]
    app_permissions: NotRequired[Permissions]
    locale: NotRequired[str]  # Always available except on PING interactions
    guild_locale: NotRequired[str]
    entitlements: list[Entitlement]
    authorizing_integration_owners: AuthorizingIntegrationOwners
    context: InteractionContextType
    attachment_size_limit: NotRequired[int]


class _BaseInteractionMetadata(TypedDict):
    """The basic fields all interaction metadata objects share"""

    id: Snowflake
    type: InteractionType
    user: User
    authorizing_integration_owners: AuthorizingIntegrationOwners
    original_response_message_id: NotRequired[Snowflake]


class ApplicationCommandInteractionMetadata(_BaseInteractionMetadata):
    target_user: NotRequired[User]
    target_message_id: NotRequired[Snowflake]


class MessageComponentInteractionMetadata(_BaseInteractionMetadata):
    interacted_message_id: Snowflake


class ModalSubmitInteractionMetadata(_BaseInteractionMetadata):
    triggering_interaction_metadata: NotRequired[
        ApplicationCommandInteractionMetadata | MessageComponentInteractionMetadata
    ]


InteractionMetadata: (
    ApplicationCommandInteractionMetadata
    | MessageComponentInteractionMetadata
    | ModalSubmitInteractionMetadata
)


class InteractionApplicationCommandCallbackData(TypedDict):
    tts: NotRequired[bool]
    content: NotRequired[str]
    embeds: NotRequired[list[Embed]]
    allowed_mentions: NotRequired[AllowedMentions]
    flags: NotRequired[int]
    components: NotRequired[list[Component]]
    attachments: NotRequired[list[Attachment]]  # Partial attachments
    poll: NotRequired[Poll]


InteractionCallbackType = Literal[
    1,  # PONG
    4,  # CHANNEL_MESSAGE_WITH_SOURCE
    5,  # DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
    6,  # DEFERRED_UPDATE_MESSAGE
    7,  # UPDATE_MESSAGE
    8,  # APPLICATION_COMMAND_AUTOCOMPLETE_RESULT
    9,  # MODAL
    10,  # PREMIUM_REQUIRED
    12,  # LAUNCH_ACTIVITY
]


class InteractionResponse(TypedDict):
    type: InteractionCallbackType
    data: NotRequired[InteractionApplicationCommandCallbackData]


class MessageInteraction(TypedDict):
    id: Snowflake
    type: InteractionType
    name: str
    user: User
    member: NotRequired[PartialMember]


class EditApplicationCommand(TypedDict):
    """The allowed fields for editing an application command."""

    name: NotRequired[str]
    name_localizations: NotRequired[dict[str, str] | None]
    description: NotRequired[str]
    description_localizations: NotRequired[dict[str, str] | None]
    options: NotRequired[list[ApplicationCommandOption]]
    default_member_permissions: NotRequired[str | None]
    dm_permission: NotRequired[bool | None]
    default_permission: NotRequired[bool | None]  # Soon to be deprecated
    integration_types: NotRequired[list[ApplicationIntegrationType]]
    contexts: NotRequired[list[InteractionContextType]]
    nsfw: NotRequired[bool]
    handler: NotRequired[CommandHandlerType]


_StringApplicationIntegrationType = Literal["0", "1"]

AuthorizingIntegrationOwners = dict[_StringApplicationIntegrationType, Snowflake]


class InteractionCallbackResponse(TypedDict):
    interaction: InteractionCallback
    resource: NotRequired[InteractionCallbackResource]


class InteractionCallback(TypedDict):
    id: Snowflake
    type: InteractionType
    activity_instance_id: NotRequired[str]
    response_message_id: NotRequired[Snowflake]
    response_message_loading: NotRequired[bool]
    response_message_ephemeral: NotRequired[bool]


class InteractionCallbackResource(TypedDict):
    type: InteractionCallbackType
    # This is not fully typed as activities are out of scope
    activity_instance: NotRequired[dict[str, str]]
    message: NotRequired[Message]
