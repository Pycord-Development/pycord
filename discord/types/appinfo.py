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

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .guild import Guild
    from .snowflake import Snowflake
    from .team import Team
    from .user import PartialUser

ApplicationIntegrationType = Literal[0, 1]
ApplicationEventWebhookStatus = Literal[1, 2, 3]


class ApplicationInstallParams(TypedDict):
    scopes: list[str]
    permissions: str


class ApplicationIntegrationTypeConfiguration(TypedDict):
    oauth2_install_params: NotRequired[ApplicationInstallParams]


class ApplicationInfo(TypedDict):
    id: Snowflake
    name: str
    icon: str | None
    description: str

    rpc_origins: NotRequired[list[str]]
    bot_public: bool
    bot_require_code_grant: bool
    hook: bool  # Whether the Discord client is allowed to hook into the application's game directly. Undocumented
    bot: NotRequired[PartialUser]
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    owner: NotRequired[PartialUser]
    verify_key: str
    team: Team | None
    guild_id: NotRequired[Snowflake]
    guild: NotRequired[Guild]
    primary_sku_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    cover_image: NotRequired[str]
    flags: NotRequired[int]
    flags_new: NotRequired[str]
    approximate_guild_count: NotRequired[int]
    approximate_user_install_count: NotRequired[int]
    approximate_user_authorization_count: NotRequired[int]
    redirect_uris: NotRequired[list[str]]
    interactions_endpoint_url: NotRequired[str | None]
    role_connections_verification_url: NotRequired[str | None]
    event_webhooks_url: NotRequired[str | None]
    event_webhooks_status: NotRequired[ApplicationEventWebhookStatus]
    event_webhooks_types: NotRequired[list[str]]
    tags: NotRequired[list[str]]
    install_params: NotRequired[ApplicationInstallParams]
    integration_types_config: NotRequired[
        dict[
            ApplicationIntegrationType,
            ApplicationIntegrationTypeConfiguration | None,
        ]
    ]
    custom_install_url: NotRequired[str]


class ReadyApplicationInfo(TypedDict):
    """Received from the gateway during the READY event."""

    id: Snowflake
    flags: int
    flags_new: str


class PartialApplicationInfo(TypedDict):
    """A partial application info object, where the docs don't specify which fields may be present."""

    id: Snowflake
    name: NotRequired[str]
    icon: NotRequired[str | None]
    description: NotRequired[str]

    rpc_origins: NotRequired[list[str]]
    bot_public: NotRequired[bool]
    bot_require_code_grant: NotRequired[bool]
    hook: bool  # Whether the Discord client is allowed to hook into the application's game directly. Undocumented
    bot: NotRequired[PartialUser]
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    owner: NotRequired[PartialUser]
    verify_key: str
    team: Team | None
    guild_id: NotRequired[Snowflake]
    guild: NotRequired[Guild]
    primary_sku_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    cover_image: NotRequired[str]
    flags: NotRequired[int]
    flags_new: NotRequired[str]
    approximate_guild_count: NotRequired[int]
    approximate_user_install_count: NotRequired[int]
    approximate_user_authorization_count: NotRequired[int]
    redirect_uris: NotRequired[list[str]]
    interactions_endpoint_url: NotRequired[str | None]
    role_connections_verification_url: NotRequired[str | None]
    event_webhooks_url: NotRequired[str | None]
    event_webhooks_status: NotRequired[ApplicationEventWebhookStatus]
    event_webhooks_types: NotRequired[list[str]]
    tags: NotRequired[list[str]]
    install_params: NotRequired[ApplicationInstallParams]
    integration_types_config: NotRequired[
        dict[
            ApplicationIntegrationType,
            ApplicationIntegrationTypeConfiguration | None,
        ]
    ]
    custom_install_url: NotRequired[str]
