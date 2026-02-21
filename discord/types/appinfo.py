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

from .guild import Guild
from .snowflake import Snowflake
from .team import Team
from .user import PartialUser

ApplicationIntegrationType = Literal[0, 1]
ApplicationEventWebhookStatus = Literal[1, 2, 3]


class AppInstallParams(TypedDict):
    scopes: list[str]
    permissions: str


class ApplicationIntegrationTypeConfiguration(TypedDict, total=False):
    oauth2_install_params: AppInstallParams


class BaseAppInfo(TypedDict):
    id: Snowflake
    name: str
    description: str
    verify_key: str

    icon: NotRequired[str | None]
    cover_image: NotRequired[str]
    guild_id: NotRequired[Snowflake]
    guild: NotRequired[Guild]
    bot: NotRequired[PartialUser]
    owner: NotRequired[PartialUser]
    team: NotRequired[Team | None]
    rpc_origins: NotRequired[list[str]]
    bot_public: NotRequired[bool]
    bot_require_code_grant: NotRequired[bool]
    terms_of_service_url: NotRequired[str | None]
    privacy_policy_url: NotRequired[str | None]
    tags: NotRequired[list[str]]
    install_params: NotRequired[AppInstallParams]
    custom_install_url: NotRequired[str]
    integration_types_config: NotRequired[
        dict[
            ApplicationIntegrationType,
            ApplicationIntegrationTypeConfiguration | None,
        ]
    ]


class AppInfo(BaseAppInfo, total=False):
    primary_sku_id: Snowflake
    slug: str
    flags: int
    approximate_guild_count: int
    approximate_user_install_count: int
    approximate_user_authorization_count: int
    redirect_uris: list[str]
    interactions_endpoint_url: str | None
    role_connections_verification_url: str | None
    event_webhooks_url: str | None
    event_webhooks_status: ApplicationEventWebhookStatus
    event_webhooks_types: list[str]


class PartialAppInfo(BaseAppInfo, total=False):
    pass
