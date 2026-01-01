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

from typing import TYPE_CHECKING, Any

from . import utils
from .asset import Asset
from .enums import ApplicationEventWebhookStatus, try_enum
from .flags import ApplicationFlags
from .permissions import Permissions

if TYPE_CHECKING:
    from .guild import Guild
    from .state import ConnectionState
    from .types.appinfo import AppInfo as AppInfoPayload
    from .types.appinfo import AppInstallParams as AppInstallParamsPayload
    from .types.appinfo import PartialAppInfo as PartialAppInfoPayload
    from .types.appinfo import Team as TeamPayload
    from .user import User

__all__ = (
    "AppInfo",
    "PartialAppInfo",
    "AppInstallParams",
    "IntegrationTypesConfig",
    "ApplicationEventWebhookStatus",
)


class AppInfo:
    """Represents the application info for the bot provided by Discord.

    Attributes
    ----------
    id: :class:`int`
        The application ID.
    name: :class:`str`
        The application name.
    owner: :class:`User`
        The application owner.
    team: Optional[:class:`Team`]
        The application's team.

        .. versionadded:: 1.3

    description: :class:`str`
        The application description.
    bot_public: :class:`bool`
        Whether the bot can be invited by anyone or if it is locked
        to the application owner.
    bot_require_code_grant: :class:`bool`
        Whether the bot requires the completion of the full OAuth2 code
        grant flow to join.
    rpc_origins: Optional[List[:class:`str`]]
        A list of RPC origin URLs, if RPC is enabled.

    verify_key: :class:`str`
        The hex encoded key for verification in interactions and the
        GameSDK's `GetTicket <https://discord.com/developers/docs/game-sdk/applications#getticket>`_.

        .. versionadded:: 1.3

    guild_id: Optional[:class:`int`]
        If this application is a game sold on Discord,
        this field will be the guild to which it has been linked to.

        .. versionadded:: 1.3

    primary_sku_id: Optional[:class:`int`]
        If this application is a game sold on Discord,
        this field will be the id of the "Game SKU" that is created,
        if it exists.

        .. versionadded:: 1.3

    slug: Optional[:class:`str`]
        If this application is a game sold on Discord,
        this field will be the URL slug that links to the store page.

        .. versionadded:: 1.3

    terms_of_service_url: Optional[:class:`str`]
        The application's terms of service URL, if set.

        .. versionadded:: 2.0

    privacy_policy_url: Optional[:class:`str`]
        The application's privacy policy URL, if set.

        .. versionadded:: 2.0

    approximate_guild_count: Optional[:class:`int`]
        The approximate count of guilds to which the app has been added, if any.

        .. versionadded:: 2.7.1

    approximate_user_install_count: Optional[:class:`int`]
        The approximate count of users who have installed the application, if any.

        .. versionadded:: 2.7

    redirect_uris: Optional[List[:class:`str`]]
        The list of redirect URIs for the application, if set.

        .. versionadded:: 2.7

    interactions_endpoint_url: Optional[:class:`str`]
        The interactions endpoint URL for the application, if set.

        .. versionadded:: 2.7.1

    role_connections_verification_url: Optional[:class:`str`]
        The role connection verification URL for the application, if set.

        .. versionadded:: 2.7.1

    install_params: Optional[:class:`AppInstallParams`]
        The settings for the application's default in-app authorization link, if set.

        .. versionadded:: 2.7.1

    integration_types_config: Optional[:class:`IntegrationTypesConfig`]
        Per-installation context configuration for guild (``0``) and user (``1``) contexts.

        .. versionadded:: 2.7.1

    event_webhooks_url: Optional[:class:`str`]
        The URL used to receive application event webhooks, if set.

        .. versionadded:: 2.7.1

    event_webhooks_status: Optional[:class:`ApplicationEventWebhookStatus`]
        The status of event webhooks for the application, if set.

        .. versionadded:: 2.7.1

    event_webhooks_types: Optional[List[:class:`str`]]
        List of event webhook types subscribed to, if set.

        .. versionadded:: 2.7.1

    tags: Optional[List[:class:`str`]]
        The list of tags describing the content and functionality of the app, if set.

        Maximium of 5 tags.

        .. versionadded:: 2.7.1

    custom_install_url: Optional[:class:`str`]
        The default custom authorization URL for the application, if set.

        .. versionadded:: 2.7.1

    approximate_user_authorization_count: Optional[:class:`int`]
        The approximate count of users who have authorized the application, if any.

        .. versionadded:: 2.7.1

    bot: Optional[:class:`User`]
        The bot user associated with this application, if any.

        .. versionadded:: 2.7.1
    """

    __slots__ = (
        "_state",
        "description",
        "id",
        "name",
        "rpc_origins",
        "bot_public",
        "bot_require_code_grant",
        "owner",
        "bot",
        "_icon",
        "_summary",
        "verify_key",
        "team",
        "guild_id",
        "primary_sku_id",
        "slug",
        "_cover_image",
        "terms_of_service_url",
        "privacy_policy_url",
        "approximate_guild_count",
        "approximate_user_install_count",
        "approximate_user_authorization_count",
        "_flags",
        "redirect_uris",
        "interactions_endpoint_url",
        "role_connections_verification_url",
        "event_webhooks_url",
        "event_webhooks_status",
        "event_webhooks_types",
        "integration_types_config",
        "install_params",
        "tags",
        "custom_install_url",
    )

    def __init__(self, state: ConnectionState, data: AppInfoPayload):
        from .team import Team

        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.description: str = data["description"]
        self._icon: str | None = data.get("icon")
        self.rpc_origins: list[str] | None = data.get("rpc_origins")
        self.bot_public: bool = data.get("bot_public", True)
        self.bot_require_code_grant: bool = data.get("bot_require_code_grant", False)
        self.owner: User | None = (
            state.create_user(owner)
            if (owner := data.get("owner")) is not None
            else None
        )

        team: TeamPayload | None = data.get("team")
        self.team: Team | None = Team(state, team) if team else None

        self._summary: str | None = data.get("summary")
        self.verify_key: str = data["verify_key"]
        self.bot: User | None = (
            state.create_user(bot) if (bot := data.get("bot")) is not None else None
        )

        self.guild_id: int | None = utils._get_as_snowflake(data, "guild_id")

        self.primary_sku_id: int | None = utils._get_as_snowflake(
            data, "primary_sku_id"
        )
        self.slug: str | None = data.get("slug")
        self._cover_image: str | None = data.get("cover_image")
        self.terms_of_service_url: str | None = data.get("terms_of_service_url")
        self.privacy_policy_url: str | None = data.get("privacy_policy_url")
        self.approximate_guild_count: int | None = data.get("approximate_guild_count")
        self.approximate_user_install_count: int | None = data.get(
            "approximate_user_install_count"
        )
        self.approximate_user_authorization_count: int | None = data.get(
            "approximate_user_authorization_count"
        )
        self._flags: int | None = data.get("flags")
        self.redirect_uris: list[str] = data.get("redirect_uris", [])
        self.interactions_endpoint_url: str | None = data.get(
            "interactions_endpoint_url"
        )
        self.role_connections_verification_url: str | None = data.get(
            "role_connections_verification_url"
        )
        self.event_webhooks_url: str | None = data.get("event_webhooks_url")
        self.event_webhooks_status: ApplicationEventWebhookStatus | None = (
            try_enum(ApplicationEventWebhookStatus, status)
            if (status := data.get("event_webhooks_status")) is not None
            else None
        )
        self.event_webhooks_types: list[str] | None = data.get("event_webhooks_types")

        self.install_params: AppInstallParams | None = (
            AppInstallParams(install_params)
            if (install_params := data.get("install_params")) is not None
            else None
        )
        self.tags: list[str] = data.get("tags", [])
        self.custom_install_url: str | None = data.get("custom_install_url")
        self.integration_types_config: IntegrationTypesConfig | None = (
            IntegrationTypesConfig.from_payload(data.get("integration_types_config"))
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id} name={self.name!r} "
            f"description={self.description!r} public={self.bot_public} "
            f"owner={self.owner!r}>"
        )

    @property
    def flags(self) -> ApplicationFlags | None:
        """The public application flags, if set.

        Returns an :class:`ApplicationFlags` instance or ``None`` when not present.

        .. versionadded:: 2.7.1
        """
        if self._flags is None:
            return None
        return ApplicationFlags._from_value(self._flags)

    async def edit(
        self,
        *,
        description: str | None = utils.MISSING,
        icon: bytes | None = utils.MISSING,
        cover_image: bytes | None = utils.MISSING,
        tags: list[str] | None = utils.MISSING,
        terms_of_service_url: str | None = utils.MISSING,
        privacy_policy_url: str | None = utils.MISSING,
        interactions_endpoint_url: str | None = utils.MISSING,
        role_connections_verification_url: str | None = utils.MISSING,
        install_params: AppInstallParams | None = utils.MISSING,
        custom_install_url: str | None = utils.MISSING,
        integration_types_config: IntegrationTypesConfig | None = utils.MISSING,
        flags: ApplicationFlags | None = utils.MISSING,
        event_webhooks_url: str | None = utils.MISSING,
        event_webhooks_status: ApplicationEventWebhookStatus = utils.MISSING,
        event_webhooks_types: list[str] | None = utils.MISSING,
    ) -> AppInfo:
        """|coro|

        Edit the current application's settings.

        .. versionadded:: 2.7.1

        Parameters
        ----------
        description: Optional[:class:`str`]
            The new application description or ``None`` to clear.
        icon: Optional[:class:`bytes`]
            New icon image. If ``bytes`` is given it will be base64 encoded automatically. Pass ``None`` to clear.
        cover_image: Optional[:class:`bytes`]
            New cover image for the store embed. If ``bytes`` is given it will be base64 encoded automatically. Pass ``None`` to clear.
        tags: Optional[List[:class:`str`]]
            List of tags for the application (max 5). Pass ``None`` to clear.
        terms_of_service_url: Optional[:class:`str`]
            The application's Terms of Service URL. Pass ``None`` to clear.
        privacy_policy_url: Optional[:class:`str`]
            The application's Privacy Policy URL. Pass ``None`` to clear.
        interactions_endpoint_url: Optional[:class:`str`]
            The interactions endpoint callback URL. Pass ``None`` to clear.
        role_connections_verification_url: Optional[:class:`str`]
            The role connection verification URL for the application. Pass ``None`` to clear.
        install_params: Optional[:class:`AppInstallParams`]
            Settings for the application's default in-app authorization link. Pass ``None`` to clear. Omit entirely to leave unchanged.
        custom_install_url: Optional[:class:`str`]
            The default custom authorization URL for the application. Pass ``None`` to clear.
        integration_types_config: Optional[:class:`IntegrationTypesConfig`]
            Object specifying per-installation context configuration (guild and/or user). You may set contexts individually
            and omit others to leave them unchanged. Pass the object with a context explicitly set to ``None`` to clear just that
            context, or pass ``None`` to clear the entire integration types configuration.
        flags: Optional[:class:`ApplicationFlags`]
            Application public flags. Pass ``None`` to clear (not typical).
        event_webhooks_url: Optional[:class:`str`]
            Event webhooks callback URL for receiving application webhook events. Pass ``None`` to clear.
        event_webhooks_status: :class:`ApplicationEventWebhookStatus`
            The desired webhook status.
        event_webhooks_types: Optional[List[:class:`str`]]
            List of webhook event types to subscribe to. Pass ``None`` to clear.

        Returns
        -------
        :class:`.AppInfo`
            The updated application information.
        """
        payload: dict[str, Any] = {}
        if description is not utils.MISSING:
            payload["description"] = description
        if icon is not utils.MISSING:
            if icon is None:
                payload["icon"] = None
            else:
                payload["icon"] = utils._bytes_to_base64_data(icon)
        if cover_image is not utils.MISSING:
            if cover_image is None:
                payload["cover_image"] = None
            else:
                payload["cover_image"] = utils._bytes_to_base64_data(cover_image)
        if tags is not utils.MISSING:
            payload["tags"] = tags
        if terms_of_service_url is not utils.MISSING:
            payload["terms_of_service_url"] = terms_of_service_url
        if privacy_policy_url is not utils.MISSING:
            payload["privacy_policy_url"] = privacy_policy_url
        if interactions_endpoint_url is not utils.MISSING:
            payload["interactions_endpoint_url"] = interactions_endpoint_url
        if role_connections_verification_url is not utils.MISSING:
            payload["role_connections_verification_url"] = (
                role_connections_verification_url
            )
        if install_params is not utils.MISSING:
            if install_params is None:
                payload["install_params"] = None
            else:
                payload["install_params"] = install_params._to_payload()
        if custom_install_url is not utils.MISSING:
            payload["custom_install_url"] = custom_install_url
        if integration_types_config is not utils.MISSING:
            if integration_types_config is None:
                payload["integration_types_config"] = None
            else:
                payload["integration_types_config"] = (
                    integration_types_config._to_payload()
                )
        if flags is not utils.MISSING:
            payload["flags"] = None if flags is None else flags.value
        if event_webhooks_url is not utils.MISSING:
            payload["event_webhooks_url"] = event_webhooks_url
        if event_webhooks_status is not utils.MISSING:
            payload["event_webhooks_status"] = event_webhooks_status.value
        if event_webhooks_types is not utils.MISSING:
            payload["event_webhooks_types"] = event_webhooks_types

        data = await self._state.http.edit_current_application_info(payload)
        return AppInfo(self._state, data)

    @property
    def icon(self) -> Asset | None:
        """Retrieves the application's icon asset, if any."""
        if self._icon is None:
            return None
        return Asset._from_icon(self._state, self.id, self._icon, path="app")

    @property
    def cover_image(self) -> Asset | None:
        """Retrieves the cover image on a store embed, if any.

        This is only available if the application is a game sold on Discord.
        """
        if self._cover_image is None:
            return None
        return Asset._from_cover_image(self._state, self.id, self._cover_image)

    @property
    def guild(self) -> Guild | None:
        """If this application is a game sold on Discord,
        this field will be the guild to which it has been linked.

        .. versionadded:: 1.3
        """
        return self._state._get_guild(self.guild_id)

    @property
    def summary(self) -> str | None:
        """If this application is a game sold on Discord,
        this field will be the summary field for the store page of its primary SKU.

        It currently returns an empty string.

        .. versionadded:: 1.3
        .. deprecated:: 2.7
        """
        utils.warn_deprecated(
            "summary",
            "description",
            reference="https://discord.com/developers/docs/resources/application#application-object-application-structure",
        )
        return self._summary


class PartialAppInfo:
    """Represents a partial AppInfo given by :func:`~discord.abc.GuildChannel.create_invite`

    .. versionadded:: 2.0

    Attributes
    ----------
    id: :class:`int`
        The application ID.
    name: :class:`str`
        The application name.
    description: :class:`str`
        The application description.
    rpc_origins: Optional[List[:class:`str`]]
        A list of RPC origin URLs, if RPC is enabled.
    summary: :class:`str`
        If this application is a game sold on Discord,
        this field will be the summary field for the store page of its primary SKU.
    verify_key: :class:`str`
        The hex encoded key for verification in interactions and the
        GameSDK's `GetTicket <https://discord.com/developers/docs/game-sdk/applications#getticket>`_.
    terms_of_service_url: Optional[:class:`str`]
        The application's terms of service URL, if set.
    privacy_policy_url: Optional[:class:`str`]
        The application's privacy policy URL, if set.
    """

    __slots__ = (
        "_state",
        "id",
        "name",
        "description",
        "rpc_origins",
        "summary",
        "verify_key",
        "terms_of_service_url",
        "privacy_policy_url",
        "_icon",
    )

    def __init__(self, *, state: ConnectionState, data: PartialAppInfoPayload):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self._icon: str | None = data.get("icon")
        self.description: str = data["description"]
        self.rpc_origins: list[str] | None = data.get("rpc_origins")
        self.summary: str = data["summary"]
        self.verify_key: str = data["verify_key"]
        self.terms_of_service_url: str | None = data.get("terms_of_service_url")
        self.privacy_policy_url: str | None = data.get("privacy_policy_url")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name!r} description={self.description!r}>"

    @property
    def icon(self) -> Asset | None:
        """Retrieves the application's icon asset, if any."""
        if self._icon is None:
            return None
        return Asset._from_icon(self._state, self.id, self._icon, path="app")


class AppInstallParams:
    """Represents the settings for the custom authorization URL of an application.

    .. versionadded:: 2.7.1

    Attributes
    ----------
    scopes: List[:class:`str`]
        The list of OAuth2 scopes for adding the application to a guild.
    permissions: :class:`Permissions`
        The permissions to request for the bot role in the guild.
    """

    __slots__ = ("scopes", "permissions")

    def __init__(self, data: AppInstallParamsPayload) -> None:
        self.scopes: list[str] = data.get("scopes", [])
        self.permissions: Permissions = Permissions(int(data["permissions"]))

    def _to_payload(self) -> dict[str, object]:
        """Serialize this object into an application install params payload.

        .. versionadded:: 2.7.1

        Returns
        -------
        Dict[str, Any]
            A dict with ``scopes`` and ``permissions`` (string form) suitable for the API.
        """
        if self.permissions.value > 0 and "bot" not in self.scopes:
            raise ValueError(
                "'bot' must be in install_params.scopes if permissions are requested"
            )
        return {
            "scopes": list(self.scopes),
            "permissions": str(self.permissions.value),
        }


class IntegrationTypesConfig:
    """Represents per-installation context configuration for an application.

    This object is used to build the payload for the ``integration_types_config`` field when editing an application.

    .. versionadded:: 2.7.1

    Parameters
    ----------
    guild: Optional[:class:`AppInstallParams`]
        The configuration for the guild installation context. Omit to leave unchanged; pass ``None`` to clear.
    user: Optional[:class:`AppInstallParams`]
        The configuration for the user installation context. Omit to leave unchanged; pass ``None`` to clear.
    """

    __slots__ = ("guild", "user")

    def __init__(
        self,
        *,
        guild: AppInstallParams | None = utils.MISSING,
        user: AppInstallParams | None = utils.MISSING,
    ) -> None:
        self.guild = guild
        self.user = user

    @staticmethod
    def _get_ctx(
        raw: dict[int | str, dict[str, object] | None] | None, key: int
    ) -> dict[str, object] | None:
        if raw is None:
            return None
        if key in raw:
            return raw[key]
        skey = str(key)
        return raw.get(skey)

    @staticmethod
    def _decode_ctx(value: dict[str, Any] | None) -> AppInstallParams | None:
        if value is None:
            return None
        params = value.get("oauth2_install_params")
        if not params:
            return None
        return AppInstallParams(params)

    @classmethod
    def from_payload(
        cls, data: dict[int | str, dict[str, Any] | None] | None
    ) -> IntegrationTypesConfig | None:
        if data is None:
            return None
        guild_ctx = cls._decode_ctx(cls._get_ctx(data, 0))
        user_ctx = cls._decode_ctx(cls._get_ctx(data, 1))
        return cls(guild=guild_ctx, user=user_ctx)

    def _encode_install_params(
        self, value: AppInstallParams | None
    ) -> dict[str, dict[str, Any]] | None:
        if value is None:
            return None
        return {"oauth2_install_params": value._to_payload()}

    def _to_payload(self) -> dict[int, dict[str, dict[str, Any]] | None]:
        """Serialize this configuration into the payload expected by the API.

        Returns
        -------
        Dict[int, Dict[str, Dict[str, Any]] | None]
            Mapping of integration context IDs to encoded install parameters, or ``None`` to clear.

        .. versionadded:: 2.7.1
        """
        payload: dict[int, dict[str, dict[str, Any]] | None] = {}
        if self.guild is not utils.MISSING:
            payload[0] = self._encode_install_params(self.guild)
        if self.user is not utils.MISSING:
            payload[1] = self._encode_install_params(self.user)
        return payload
