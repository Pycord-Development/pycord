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

import asyncio
from typing import TYPE_CHECKING, Any, Coroutine, Union

from . import utils
from .channel import ChannelType, PartialMessageable, _threaded_channel_factory
from .enums import (
    InteractionContextType,
    InteractionResponseType,
    InteractionType,
    try_enum,
)
from .errors import ClientException, InteractionResponded, InvalidArgument
from .file import File
from .flags import MessageFlags
from .guild import Guild
from .member import Member
from .message import Attachment, Message
from .monetization import Entitlement
from .object import Object
from .permissions import Permissions
from .user import User
from .webhook.async_ import (
    Webhook,
    WebhookMessage,
    async_context,
    handle_message_parameters,
)

__all__ = (
    "Interaction",
    "InteractionMessage",
    "InteractionResponse",
    "MessageInteraction",
    "InteractionMetadata",
    "AuthorizingIntegrationOwners",
)

if TYPE_CHECKING:
    from aiohttp import ClientSession

    from .channel import (
        CategoryChannel,
        DMChannel,
        ForumChannel,
        GroupChannel,
        StageChannel,
        TextChannel,
        VoiceChannel,
    )
    from .client import Client
    from .commands import OptionChoice
    from .embeds import Embed
    from .mentions import AllowedMentions
    from .poll import Poll
    from .state import ConnectionState
    from .threads import Thread
    from .types.interactions import Interaction as InteractionPayload
    from .types.interactions import InteractionData
    from .types.interactions import InteractionMetadata as InteractionMetadataPayload
    from .types.interactions import MessageInteraction as MessageInteractionPayload
    from .ui.modal import Modal
    from .ui.view import View

    InteractionChannel = Union[
        VoiceChannel,
        StageChannel,
        TextChannel,
        ForumChannel,
        CategoryChannel,
        Thread,
        DMChannel,
        GroupChannel,
        PartialMessageable,
    ]

MISSING: Any = utils.MISSING


class Interaction:
    """Represents a Discord interaction.

    An interaction happens when a user does an action that needs to
    be notified. Current examples are application commands, components, and modals.

    .. versionadded:: 2.0

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel: Optional[Union[:class:`abc.GuildChannel`, :class:`abc.PrivateChannel`, :class:`Thread`]]
        The channel the interaction was sent from.
    channel_id: Optional[:class:`int`]
        The ID of the channel the interaction was sent from.
    application_id: :class:`int`
        The application ID that the interaction was for.
    user: Optional[Union[:class:`User`, :class:`Member`]]
        The user or member that sent the interaction. Will be `None` in PING interactions.
    message: Optional[:class:`Message`]
        The message that sent this interaction.
    token: :class:`str`
        The token to continue the interaction. These are valid
        for 15 minutes.
    data: :class:`dict`
        The raw interaction data.
    locale: :class:`str`
        The user's locale.
    guild_locale: :class:`str`
        The guilds preferred locale, if invoked in a guild.
    custom_id: Optional[:class:`str`]
        The custom ID for the interaction.
    entitlements: list[:class:`Entitlement`]
        Entitlements that apply to the invoking user, showing access to premium SKUs.

        .. versionadded:: 2.5
    authorizing_integration_owners: :class:`AuthorizingIntegrationOwners`
        Contains the entities (users or guilds) that authorized this interaction.

        .. versionadded:: 2.6
    context: Optional[:class:`InteractionContextType`]
        The context in which this command was executed.

        .. versionadded:: 2.6
    """

    __slots__: tuple[str, ...] = (
        "id",
        "type",
        "guild_id",
        "channel",
        "channel_id",
        "data",
        "application_id",
        "message",
        "user",
        "locale",
        "guild_locale",
        "token",
        "version",
        "custom_id",
        "entitlements",
        "context",
        "authorizing_integration_owners",
        "_channel_data",
        "_message_data",
        "_guild_data",
        "_guild",
        "_permissions",
        "_app_permissions",
        "_state",
        "_session",
        "_original_response",
        "_cs_app_permissions",
        "_cs_response",
        "_cs_followup",
        "_cs_channel",
    )

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        self._state: ConnectionState = state
        self._session: ClientSession = state.http._HTTPClient__session
        self._original_response: InteractionMessage | None = None
        self._from_data(data)

    def _from_data(self, data: InteractionPayload):
        self.id: int = int(data["id"])
        self.type: InteractionType = try_enum(InteractionType, data["type"])
        self.data: InteractionData | None = data.get("data")
        self.token: str = data["token"]
        self.version: int = data["version"]
        self.channel_id: int | None = utils._get_as_snowflake(data, "channel_id")
        self.guild_id: int | None = utils._get_as_snowflake(data, "guild_id")
        self.application_id: int = int(data["application_id"])
        self.locale: str | None = data.get("locale")
        self.guild_locale: str | None = data.get("guild_locale")
        self.custom_id: str | None = (
            self.data.get("custom_id") if self.data is not None else None
        )
        self._app_permissions: int = int(data.get("app_permissions", 0))
        self.entitlements: list[Entitlement] = [
            Entitlement(data=e, state=self._state) for e in data.get("entitlements", [])
        ]
        self.authorizing_integration_owners: AuthorizingIntegrationOwners = (
            AuthorizingIntegrationOwners(
                data=data["authorizing_integration_owners"], state=self._state
            )
            if "authorizing_integration_owners" in data
            else AuthorizingIntegrationOwners(data={}, state=self._state)
        )
        self.context: InteractionContextType | None = (
            try_enum(InteractionContextType, data["context"])
            if "context" in data
            else None
        )

        self.message: Message | None = None
        self.channel = None

        self.user: User | Member | None = None
        self._permissions: int = 0

        self._guild: Guild | None = None
        self._guild_data = data.get("guild")
        if self.guild is None and self._guild_data:
            self._guild = Guild(data=self._guild_data, state=self._state)

        # TODO: there's a potential data loss here
        if self.guild_id:
            guild = (
                self.guild
                or self._state._get_guild(self.guild_id)
                or Object(id=self.guild_id)
            )
            try:
                member = data["member"]  # type: ignore
            except KeyError:
                pass
            else:
                self._permissions = int(member.get("permissions", 0))
                if not isinstance(guild, Object):
                    cache_flag = self._state.member_cache_flags.interaction
                    self.user = guild._get_and_update_member(
                        member, int(member["user"]["id"]), cache_flag
                    )
                else:
                    self.user = Member(state=self._state, data=member, guild=guild)
        else:
            try:
                self.user = User(state=self._state, data=data["user"])
            except KeyError:
                pass

        if channel := data.get("channel"):
            if (ch_type := channel.get("type")) is not None:
                factory, ch_type = _threaded_channel_factory(ch_type)

                if ch_type in (ChannelType.group, ChannelType.private):
                    self.channel = factory(
                        me=self.user, data=channel, state=self._state
                    )
                elif self.guild:
                    self.channel = factory(
                        guild=self.guild, state=self._state, data=channel
                    )
        else:
            self.channel = self.cached_channel

        self._channel_data = channel

        if message_data := data.get("message"):
            self.message = Message(
                state=self._state, channel=self.channel, data=message_data
            )

        self._message_data = message_data

    @property
    def client(self) -> Client:
        """Returns the client that sent the interaction."""
        return self._state._get_client()

    @property
    def guild(self) -> Guild | None:
        """The guild the interaction was sent from."""
        if self._guild:
            return self._guild
        return self._state and self._state._get_guild(self.guild_id)

    def is_command(self) -> bool:
        """Indicates whether the interaction is an application command."""
        return self.type == InteractionType.application_command

    def is_component(self) -> bool:
        """Indicates whether the interaction is a message component."""
        return self.type == InteractionType.component

    @utils.cached_slot_property("_cs_channel")
    def cached_channel(self) -> InteractionChannel | None:
        """The channel the
        interaction was sent from.

        Note that due to a Discord limitation, DM channels are not resolved since there is
        no data to complete them. These are :class:`PartialMessageable` instead.
        """
        guild = self.guild
        channel = guild and guild._resolve_channel(self.channel_id)
        if channel is None:
            if self.channel_id is not None:
                type = (
                    ChannelType.text
                    if self.guild_id is not None
                    else ChannelType.private
                )
                return PartialMessageable(
                    state=self._state, id=self.channel_id, type=type
                )
            return None
        return channel

    @property
    def permissions(self) -> Permissions:
        """The resolved permissions of the member in the channel, including overwrites.

        In a non-guild context where this doesn't apply, an empty permissions object is returned.
        """
        return Permissions(self._permissions)

    @utils.cached_slot_property("_cs_app_permissions")
    def app_permissions(self) -> Permissions:
        """The resolved permissions of the application in the channel, including overwrites."""
        return Permissions(self._app_permissions)

    @utils.cached_slot_property("_cs_response")
    def response(self) -> InteractionResponse:
        """Returns an object responsible for handling responding to the interaction.

        A response can only be done once. If secondary messages need to be sent, consider using :attr:`followup`
        instead.
        """
        return InteractionResponse(self)

    @utils.cached_slot_property("_cs_followup")
    def followup(self) -> Webhook:
        """Returns the followup webhook for followup interactions."""
        payload = {
            "id": self.application_id,
            "type": 3,
            "token": self.token,
        }
        return Webhook.from_state(data=payload, state=self._state)

    async def original_response(self) -> InteractionMessage:
        """|coro|

        Fetches the original interaction response message associated with the interaction.

        If the interaction response was :meth:`InteractionResponse.send_message` then this would
        return the message that was sent using that response. Otherwise, this would return
        the message that triggered the interaction.

        Repeated calls to this will return a cached value.

        Returns
        -------
        InteractionMessage
            The original interaction response message.

        Raises
        ------
        HTTPException
            Fetching the original response message failed.
        ClientException
            The channel for the message could not be resolved.
        """

        if self._original_response is not None:
            return self._original_response

        # TODO: fix later to not raise?
        channel = self.channel
        if channel is None:
            raise ClientException("Channel for message could not be resolved")

        adapter = async_context.get()
        http = self._state.http
        data = await adapter.get_original_interaction_response(
            application_id=self.application_id,
            token=self.token,
            session=self._session,
            proxy=http.proxy,
            proxy_auth=http.proxy_auth,
        )
        state = _InteractionMessageState(self, self._state)
        message = InteractionMessage(state=state, channel=channel, data=data)  # type: ignore
        self._original_response = message
        return message

    @utils.deprecated("Interaction.original_response", "2.2")
    async def original_message(self):
        """An alias for :meth:`original_response`.

        Returns
        -------
        InteractionMessage
            The original interaction response message.

        Raises
        ------
        HTTPException
            Fetching the original response message failed.
        ClientException
            The channel for the message could not be resolved.
        """
        return await self.original_response()

    async def edit_original_response(
        self,
        *,
        content: str | None = MISSING,
        embeds: list[Embed] = MISSING,
        embed: Embed | None = MISSING,
        file: File = MISSING,
        files: list[File] = MISSING,
        attachments: list[Attachment] = MISSING,
        view: View | None = MISSING,
        allowed_mentions: AllowedMentions | None = None,
        delete_after: float | None = None,
        suppress: bool = False,
    ) -> InteractionMessage:
        """|coro|

        Edits the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.edit` in case
        you do not want to fetch the message and save an HTTP request.

        This method is also the only way to edit the original message if
        the message sent was ephemeral.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content to edit the message with or ``None`` to clear it.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of files to send with the content. This cannot be mixed with the
            ``file`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        view: Optional[:class:`~discord.ui.View`]
            The updated view to update this message with. If ``None`` is passed then
            the view is removed.
        delete_after: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background
            before deleting the message we just edited. If the deletion fails,
            then it is silently ignored.
        suppress: :class:`bool`
            Whether to suppress embeds for the message.

        Returns
        -------
        :class:`InteractionMessage`
            The newly edited message.

        Raises
        ------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.
        """

        previous_mentions: AllowedMentions | None = self._state.allowed_mentions
        params = handle_message_parameters(
            content=content,
            file=file,
            files=files,
            attachments=attachments,
            embed=embed,
            embeds=embeds,
            view=view,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=previous_mentions,
            suppress=suppress,
        )
        adapter = async_context.get()
        http = self._state.http
        data = await adapter.edit_original_interaction_response(
            self.application_id,
            self.token,
            session=self._session,
            proxy=http.proxy,
            proxy_auth=http.proxy_auth,
            payload=params.payload,
            multipart=params.multipart,
            files=params.files,
        )

        # The message channel types should always match
        state = _InteractionMessageState(self, self._state)
        message = InteractionMessage(state=state, channel=self.channel, data=data)  # type: ignore
        if view and not view.is_finished():
            view.message = message
            self._state.store_view(view, message.id)

        if delete_after is not None:
            await self.delete_original_response(delay=delete_after)

        return message

    @utils.deprecated("Interaction.edit_original_response", "2.2")
    async def edit_original_message(self, **kwargs):
        """An alias for :meth:`edit_original_response`.

        Returns
        -------
        :class:`InteractionMessage`
            The newly edited message.

        Raises
        ------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.
        """
        return await self.edit_original_response(**kwargs)

    async def delete_original_response(self, *, delay: float | None = None) -> None:
        """|coro|

        Deletes the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.delete` in case
        you do not want to fetch the message and save an HTTP request.

        Parameters
        ----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait before deleting the message.
            The waiting is done in the background and deletion failures are ignored.

        Raises
        ------
        HTTPException
            Deleting the message failed.
        Forbidden
            Deleted a message that is not yours.
        """
        adapter = async_context.get()
        http = self._state.http
        func = adapter.delete_original_interaction_response(
            self.application_id,
            self.token,
            session=self._session,
            proxy=http.proxy,
            proxy_auth=http.proxy_auth,
        )

        if delay is not None:
            utils.delay_task(delay, func)
        else:
            await func

    @utils.deprecated("Interaction.delete_original_response", "2.2")
    async def delete_original_message(self, **kwargs):
        """An alias for :meth:`delete_original_response`.

        Raises
        ------
        HTTPException
            Deleting the message failed.
        Forbidden
            Deleted a message that is not yours.
        """
        return await self.delete_original_response(**kwargs)

    async def respond(self, *args, **kwargs) -> Interaction | WebhookMessage:
        """|coro|

        Sends either a response or a message using the followup webhook determined by whether the interaction
        has been responded to or not.

        Returns
        -------
        Union[:class:`discord.Interaction`, :class:`discord.WebhookMessage`]:
            The response, its type depending on whether it's an interaction response or a followup.
        """
        try:
            if not self.response.is_done():
                return await self.response.send_message(*args, **kwargs)
            else:
                return await self.followup.send(*args, **kwargs)
        except InteractionResponded:
            return await self.followup.send(*args, **kwargs)

    async def edit(self, *args, **kwargs) -> InteractionMessage | None:
        """|coro|

        Either respond to the interaction with an edit_message or edits the existing response, determined by
        whether the interaction has been responded to or not.

        Returns
        -------
        Union[:class:`discord.InteractionMessage`, :class:`discord.WebhookMessage`]:
            The response, its type depending on whether it's an interaction response or a followup.
        """
        try:
            if not self.response.is_done():
                return await self.response.edit_message(*args, **kwargs)
            else:
                return await self.edit_original_response(*args, **kwargs)
        except InteractionResponded:
            return await self.edit_original_response(*args, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        """
        Converts this interaction object into a dict.

        Returns
        -------
        Dict[:class:`str`, Any]
            A dictionary of :class:`str` interaction keys bound to the respective value.
        """

        data = {
            "id": self.id,
            "application_id": self.application_id,
            "type": self.type.value,
            "token": self.token,
            "version": self.version,
        }

        if self.data is not None:
            data["data"] = self.data
            if (resolved := self.data.get("resolved")) and self.user is not None:
                if (users := resolved.get("users")) and (
                    user := users.get(self.user.id)
                ):
                    data["user"] = user
                if (members := resolved.get("members")) and (
                    member := members.get(self.user.id)
                ):
                    data["member"] = member

        if self.guild_id is not None:
            data["guild_id"] = self.guild_id

        if self.channel_id is not None:
            data["channel_id"] = self.channel_id

        if self.locale:
            data["locale"] = self.locale

        if self.guild_locale:
            data["guild_locale"] = self.guild_locale

        if self._message_data:
            data["message"] = self._message_data

        return data


class InteractionResponse:
    """Represents a Discord interaction response.

    This type can be accessed through :attr:`Interaction.response`.

    .. versionadded:: 2.0
    """

    __slots__: tuple[str, ...] = (
        "_responded",
        "_parent",
        "_response_lock",
    )

    def __init__(self, parent: Interaction):
        self._parent: Interaction = parent
        self._responded: bool = False
        self._response_lock = asyncio.Lock()

    def is_done(self) -> bool:
        """Indicates whether an interaction response has been done before.

        An interaction can only be responded to once.
        """
        return self._responded

    async def defer(self, *, ephemeral: bool = False, invisible: bool = True) -> None:
        """|coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        This can only be used with the following interaction types:

        - :attr:`InteractionType.application_command`
        - :attr:`InteractionType.component`
        - :attr:`InteractionType.modal_submit`

        .. note::
            The follow-up response will also be non-ephemeral if the `ephemeral`
            argument is ``False``, and ephemeral if ``True``.

        Parameters
        ----------
        ephemeral: :class:`bool`
            Indicates whether the deferred message will eventually be ephemeral.
            This only applies to :attr:`InteractionType.application_command` interactions,
            or if ``invisible`` is ``False``.
        invisible: :class:`bool`
            Indicates whether the deferred type should be 'invisible'
            (:attr:`InteractionResponseType.deferred_message_update`)
            instead of 'thinking' (:attr:`InteractionResponseType.deferred_channel_message`).
            In the Discord UI, this is represented as the bot thinking of a response. You must
            eventually send a followup message via :attr:`Interaction.followup` to make this thinking state go away.
            This parameter does not apply to interactions of type :attr:`InteractionType.application_command`.

        Raises
        ------
        HTTPException
            Deferring the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        defer_type: int = 0
        data: dict[str, Any] | None = None
        parent = self._parent
        if (
            parent.type is InteractionType.component
            or parent.type is InteractionType.modal_submit
        ):
            defer_type = (
                InteractionResponseType.deferred_message_update.value
                if invisible
                else InteractionResponseType.deferred_channel_message.value
            )
            if not invisible and ephemeral:
                data = {"flags": 64}
        elif parent.type is InteractionType.application_command:
            defer_type = InteractionResponseType.deferred_channel_message.value
            if ephemeral:
                data = {"flags": 64}

        if defer_type:
            adapter = async_context.get()
            http = parent._state.http
            await self._locked_response(
                adapter.create_interaction_response(
                    parent.id,
                    parent.token,
                    session=parent._session,
                    type=defer_type,
                    data=data,
                    proxy=http.proxy,
                    proxy_auth=http.proxy_auth,
                )
            )
            self._responded = True

    async def pong(self) -> None:
        """|coro|

        Pongs the ping interaction.

        This should rarely be used.

        Raises
        ------
        HTTPException
            Ponging the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        if parent.type is InteractionType.ping:
            adapter = async_context.get()
            http = parent._state.http
            await self._locked_response(
                adapter.create_interaction_response(
                    parent.id,
                    parent.token,
                    session=parent._session,
                    proxy=http.proxy,
                    proxy_auth=http.proxy_auth,
                    type=InteractionResponseType.pong.value,
                )
            )
            self._responded = True

    async def send_message(
        self,
        content: Any | None = None,
        *,
        embed: Embed = None,
        embeds: list[Embed] = None,
        view: View = None,
        tts: bool = False,
        ephemeral: bool = False,
        allowed_mentions: AllowedMentions = None,
        file: File = None,
        files: list[File] = None,
        poll: Poll = None,
        delete_after: float = None,
    ) -> Interaction:
        """|coro|

        Responds to this interaction by sending a message.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the message to send.
        embeds: List[:class:`Embed`]
            A list of embeds to send with the content. Maximum of 10. This cannot
            be mixed with the ``embed`` parameter.
        embed: :class:`Embed`
            The rich embed for the content to send. This cannot be mixed with
            ``embeds`` parameter.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        view: :class:`discord.ui.View`
            The view to send with the message.
        ephemeral: :class:`bool`
            Indicates if the message should only be visible to the user who started the interaction.
            If a view is sent with an ephemeral message, and it has no timeout set then the timeout
            is set to 15 minutes.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent.
        file: :class:`File`
            The file to upload.
        files: List[:class:`File`]
            A list of files to upload. Must be a maximum of 10.
        poll: :class:`Poll`
            The poll to send.

            .. versionadded:: 2.6

        Returns
        -------
        :class:`.Interaction`
            The interaction object associated with the sent message.

        Raises
        ------
        HTTPException
            Sending the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        ValueError
            The length of ``embeds`` was invalid.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        payload: dict[str, Any] = {
            "tts": tts,
        }

        if embed is not None and embeds is not None:
            raise TypeError("cannot mix embed and embeds keyword arguments")

        if embed is not None:
            embeds = [embed]

        if embeds:
            if len(embeds) > 10:
                raise ValueError("embeds cannot exceed maximum of 10 elements")
            payload["embeds"] = [e.to_dict() for e in embeds]

        if content is not None:
            payload["content"] = str(content)

        if ephemeral:
            payload["flags"] = 64

        if view is not None:
            payload["components"] = view.to_components()

        if poll is not None:
            payload["poll"] = poll.to_dict()

        state = self._parent._state

        if allowed_mentions is None:
            payload["allowed_mentions"] = (
                state.allowed_mentions and state.allowed_mentions.to_dict()
            )

        elif state.allowed_mentions is not None:
            payload["allowed_mentions"] = state.allowed_mentions.merge(
                allowed_mentions
            ).to_dict()
        else:
            payload["allowed_mentions"] = allowed_mentions.to_dict()
        if file is not None and files is not None:
            raise InvalidArgument("cannot pass both file and files parameter to send()")

        if file is not None:
            if not isinstance(file, File):
                raise InvalidArgument("file parameter must be File")
            else:
                files = [file]

        if files is not None:
            if len(files) > 10:
                raise InvalidArgument(
                    "files parameter must be a list of up to 10 elements"
                )
            elif not all(isinstance(file, File) for file in files):
                raise InvalidArgument("files parameter must be a list of File")

        parent = self._parent
        adapter = async_context.get()
        http = parent._state.http
        try:
            await self._locked_response(
                adapter.create_interaction_response(
                    parent.id,
                    parent.token,
                    session=parent._session,
                    type=InteractionResponseType.channel_message.value,
                    proxy=http.proxy,
                    proxy_auth=http.proxy_auth,
                    data=payload,
                    files=files,
                )
            )
        finally:
            if files:
                for file in files:
                    file.close()

        if view is not None:
            if ephemeral and view.timeout is None:
                view.timeout = 15 * 60.0

            view.parent = self._parent
            self._parent._state.store_view(view)

        self._responded = True
        if delete_after is not None:
            await self._parent.delete_original_response(delay=delete_after)
        return self._parent

    async def edit_message(
        self,
        *,
        content: Any | None = MISSING,
        embed: Embed | None = MISSING,
        embeds: list[Embed] = MISSING,
        file: File = MISSING,
        files: list[File] = MISSING,
        attachments: list[Attachment] = MISSING,
        view: View | None = MISSING,
        delete_after: float | None = None,
        suppress: bool | None = MISSING,
        allowed_mentions: AllowedMentions | None = None,
    ) -> None:
        """|coro|

        Responds to this interaction by editing the original message of
        a component or modal interaction.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The new content to replace the message with. ``None`` removes the content.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        file: :class:`File`
            A new file to add to the message. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of new files to add to the message. Must be a maximum of 10. This
            cannot be mixed with the ``file`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        view: Optional[:class:`~discord.ui.View`]
            The updated view to update this message with. If ``None`` is passed then
            the view is removed.
        delete_after: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background
            before deleting the message we just edited. If the deletion fails,
            then it is silently ignored.
        suppress: Optional[:class:`bool`]
            Whether to suppress embeds for the message.
        allowed_mentions: Optional[:class:`~discord.AllowedMentions`]
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
            are used instead.

        Raises
        ------
        HTTPException
            Editing the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        msg = parent.message
        state = parent._state
        message_id = msg.id if msg else None
        if parent.type not in (InteractionType.component, InteractionType.modal_submit):
            return

        payload = {}
        if content is not MISSING:
            payload["content"] = None if content is None else str(content)
        if embed is not MISSING and embeds is not MISSING:
            raise TypeError("cannot mix both embed and embeds keyword arguments")

        if embed is not MISSING:
            embeds = [] if embed is None else [embed]
        if embeds is not MISSING:
            payload["embeds"] = [e.to_dict() for e in embeds]

        if attachments is not MISSING:
            payload["attachments"] = [a.to_dict() for a in attachments]

        if view is not MISSING:
            state.prevent_view_updates_for(message_id)
            payload["components"] = [] if view is None else view.to_components()

        if file is not MISSING and files is not MISSING:
            raise InvalidArgument(
                "cannot pass both file and files parameter to edit_message()"
            )

        if file is not MISSING:
            if not isinstance(file, File):
                raise InvalidArgument("file parameter must be a File")
            else:
                files = [file]
                if "attachments" not in payload:
                    # we keep previous attachments when adding a new file
                    payload["attachments"] = [a.to_dict() for a in msg.attachments]

        if files is not MISSING:
            if len(files) > 10:
                raise InvalidArgument(
                    "files parameter must be a list of up to 10 elements"
                )
            elif not all(isinstance(file, File) for file in files):
                raise InvalidArgument("files parameter must be a list of File")
            if "attachments" not in payload:
                # we keep previous attachments when adding new files
                payload["attachments"] = [a.to_dict() for a in msg.attachments]

        if suppress is not MISSING:
            flags = MessageFlags._from_value(self._parent.message.flags.value)
            flags.suppress_embeds = suppress
            payload["flags"] = flags.value

        if allowed_mentions is None:
            payload["allowed_mentions"] = (
                state.allowed_mentions and state.allowed_mentions.to_dict()
            )

        elif state.allowed_mentions is not None:
            payload["allowed_mentions"] = state.allowed_mentions.merge(
                allowed_mentions
            ).to_dict()
        else:
            payload["allowed_mentions"] = allowed_mentions.to_dict()

        adapter = async_context.get()
        http = parent._state.http
        try:
            await self._locked_response(
                adapter.create_interaction_response(
                    parent.id,
                    parent.token,
                    session=parent._session,
                    type=InteractionResponseType.message_update.value,
                    proxy=http.proxy,
                    proxy_auth=http.proxy_auth,
                    data=payload,
                    files=files,
                )
            )
        finally:
            if files:
                for file in files:
                    file.close()

        if view and not view.is_finished():
            view.message = msg
            state.store_view(view, message_id)

        self._responded = True
        if delete_after is not None:
            await self._parent.delete_original_response(delay=delete_after)

    async def send_autocomplete_result(
        self,
        *,
        choices: list[OptionChoice],
    ) -> None:
        """|coro|
        Responds to this interaction by sending the autocomplete choices.

        Parameters
        ----------
        choices: List[:class:`OptionChoice`]
            A list of choices.

        Raises
        ------
        HTTPException
            Sending the result failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent

        if parent.type is not InteractionType.auto_complete:
            return

        payload = {"choices": [c.to_dict() for c in choices]}

        adapter = async_context.get()
        http = parent._state.http
        await self._locked_response(
            adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                proxy=http.proxy,
                proxy_auth=http.proxy_auth,
                type=InteractionResponseType.auto_complete_result.value,
                data=payload,
            )
        )

        self._responded = True

    async def send_modal(self, modal: Modal) -> Interaction:
        """|coro|
        Responds to this interaction by sending a modal dialog.
        This cannot be used to respond to another modal dialog submission.

        Parameters
        ----------
        modal: :class:`discord.ui.Modal`
            The modal dialog to display to the user.

        Raises
        ------
        HTTPException
            Sending the modal failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent

        payload = modal.to_dict()
        adapter = async_context.get()
        http = parent._state.http
        await self._locked_response(
            adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                proxy=http.proxy,
                proxy_auth=http.proxy_auth,
                type=InteractionResponseType.modal.value,
                data=payload,
            )
        )
        self._responded = True
        self._parent._state.store_modal(modal, self._parent.user.id)
        return self._parent

    @utils.deprecated("a button with type ButtonType.premium", "2.6")
    async def premium_required(self) -> Interaction:
        """|coro|

        Responds to this interaction by sending a premium required message.

        .. deprecated:: 2.6

            A button with type :attr:`ButtonType.premium` should be used instead.

        Raises
        ------
        HTTPException
            Sending the message failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent

        adapter = async_context.get()
        http = parent._state.http
        await self._locked_response(
            adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                proxy=http.proxy,
                proxy_auth=http.proxy_auth,
                type=InteractionResponseType.premium_required.value,
            )
        )
        self._responded = True
        return self._parent

    async def _locked_response(self, coro: Coroutine[Any, Any, Any]) -> None:
        """|coro|

        Wraps a response and makes sure that it's locked while executing.

        Parameters
        ----------
        coro: Coroutine[Any]
            The coroutine to wrap.

        Raises
        ------
        InteractionResponded
            This interaction has already been responded to before.
        """
        async with self._response_lock:
            if self.is_done():
                coro.close()  # cleanup un-awaited coroutine
                raise InteractionResponded(self._parent)
            await coro


class _InteractionMessageState:
    __slots__ = ("_parent", "_interaction")

    def __init__(self, interaction: Interaction, parent: ConnectionState):
        self._interaction: Interaction = interaction
        self._parent: ConnectionState = parent

    def _get_guild(self, guild_id):
        return self._parent._get_guild(guild_id)

    def store_user(self, data):
        return self._parent.store_user(data)

    def create_user(self, data):
        return self._parent.create_user(data)

    @property
    def http(self):
        return self._parent.http

    def __getattr__(self, attr):
        return getattr(self._parent, attr)


class InteractionMessage(Message):
    """Represents the original interaction response message.

    This allows you to edit or delete the message associated with
    the interaction response. To retrieve this object see :meth:`Interaction.original_response`.

    This inherits from :class:`discord.Message` with changes to
    :meth:`edit` and :meth:`delete` to work.

    .. versionadded:: 2.0
    """

    __slots__ = ()
    _state: _InteractionMessageState

    async def edit(
        self,
        content: str | None = MISSING,
        embeds: list[Embed] = MISSING,
        embed: Embed | None = MISSING,
        file: File = MISSING,
        files: list[File] = MISSING,
        attachments: list[Attachment] = MISSING,
        view: View | None = MISSING,
        allowed_mentions: AllowedMentions | None = None,
        delete_after: float | None = None,
        suppress: bool | None = MISSING,
    ) -> InteractionMessage:
        """|coro|

        Edits the message.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content to edit the message with or ``None`` to clear it.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of files to send with the content. This cannot be mixed with the
            ``file`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        view: Optional[:class:`~discord.ui.View`]
            The updated view to update this message with. If ``None`` is passed then
            the view is removed.
        delete_after: Optional[:class:`float`]
            If provided, the number of seconds to wait in the background
            before deleting the message we just edited. If the deletion fails,
            then it is silently ignored.
        suppress: Optional[:class:`bool`]
            Whether to suppress embeds for the message.

        Returns
        -------
        :class:`InteractionMessage`
            The newly edited message.

        Raises
        ------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.
        """
        if attachments is MISSING:
            attachments = self.attachments or MISSING
        if suppress is MISSING:
            suppress = self.flags.suppress_embeds
        return await self._state._interaction.edit_original_response(
            content=content,
            embeds=embeds,
            embed=embed,
            file=file,
            files=files,
            attachments=attachments,
            view=view,
            allowed_mentions=allowed_mentions,
            delete_after=delete_after,
            suppress=suppress,
        )

    async def delete(self, *, delay: float | None = None) -> None:
        """|coro|

        Deletes the message.

        Parameters
        ----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait before deleting the message.
            The waiting is done in the background and deletion failures are ignored.

        Raises
        ------
        Forbidden
            You do not have proper permissions to delete the message.
        NotFound
            The message was deleted already.
        HTTPException
            Deleting the message failed.
        """
        await self._state._interaction.delete_original_response(delay=delay)


class MessageInteraction:
    """Represents a Discord message interaction.

    This is sent on the message object when the message is a response
    to an interaction without an existing message e.g. application command.

    .. versionadded:: 2.0

    .. deprecated:: 2.6

        See :class:`InteractionMetadata`.

    .. note::
        Responses to message components do not include this property.

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    name: :class:`str`
        The name of the invoked application command.
    user: :class:`User`
        The user that sent the interaction.
    data: :class:`dict`
        The raw interaction data.
    """

    __slots__: tuple[str, ...] = ("id", "type", "name", "user", "data", "_state")

    def __init__(self, *, data: MessageInteractionPayload, state: ConnectionState):
        self._state = state
        self.data = data
        self.id: int = int(data["id"])
        self.type: InteractionType = data["type"]
        self.name: str = data["name"]
        self.user: User = self._state.store_user(data["user"])


class InteractionMetadata:
    """Represents metadata about an interaction.

    This is sent on the message object when the message is related to an interaction

    .. versionadded:: 2.6

    Attributes
    ----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    user: :class:`User`
        The user that sent the interaction.
    authorizing_integration_owners: :class:`AuthorizingIntegrationOwners`
        The authorizing user or server for the installation(s) relevant to the interaction.
    original_response_message_id: Optional[:class:`int`]
        The ID of the original response message. Only present on interaction follow-up messages.
    interacted_message_id: Optional[:class:`int`]
        The ID of the message that triggered the interaction. Only present on interactions of type
        :attr:`InteractionType.component`.
    triggering_interaction_metadata: Optional[:class:`InteractionMetadata`]
        The metadata of the interaction that opened the model. Only present on interactions of type
        :attr:`InteractionType.modal_submit`.
    """

    __slots__: tuple[str, ...] = (
        "id",
        "type",
        "user",
        "authorizing_integration_owners",
        "original_response_message_id",
        "interacted_message_id",
        "triggering_interaction_metadata",
        "_state",
        "_cs_original_response_message",
        "_cs_interacted_message",
    )

    def __init__(self, *, data: InteractionMetadataPayload, state: ConnectionState):
        self._state = state
        self.id: int = int(data["id"])
        self.type: InteractionType = try_enum(InteractionType, data["type"])
        self.user: User = User(state=state, data=data["user"])
        self.authorizing_integration_owners: AuthorizingIntegrationOwners = (
            AuthorizingIntegrationOwners(data["authorizing_integration_owners"], state)
        )
        self.original_response_message_id: int | None = utils._get_as_snowflake(
            data, "original_response_message_id"
        )
        self.interacted_message_id: int | None = utils._get_as_snowflake(
            data, "interacted_message_id"
        )
        self.triggering_interaction_metadata: InteractionMetadata | None = None
        if tim := data.get("triggering_interaction_metadata"):
            self.triggering_interaction_metadata = InteractionMetadata(
                data=tim, state=state
            )

    def __repr__(self):
        return (
            f"<InteractionMetadata id={self.id} type={self.type!r} user={self.user!r}>"
        )

    @utils.cached_slot_property("_cs_original_response_message")
    def original_response_message(self) -> Message | None:
        """Optional[:class:`Message`]: The original response message.
        Returns ``None`` if the message is not in cache, or if :attr:`original_response_message_id` is ``None``.
        """
        if not self.original_response_message_id:
            return None
        return self._state._get_message(self.original_response_message_id)

    @utils.cached_slot_property("_cs_interacted_message")
    def interacted_message(self) -> Message | None:
        """Optional[:class:`Message`]: The message that triggered the interaction.
        Returns ``None`` if the message is not in cache, or if :attr:`interacted_message_id` is ``None``.
        """
        if not self.interacted_message_id:
            return None
        return self._state._get_message(self.interacted_message_id)


class AuthorizingIntegrationOwners:
    """Contains details on the authorizing user or server for the installation(s) relevant to the interaction.

    .. versionadded:: 2.6

    Attributes
    ----------
    user_id: :class:`int` | None
        The ID of the user that authorized the integration.
    guild_id: :class:`int` | None
        The ID of the guild that authorized the integration.
        This will be ``0`` if the integration was triggered
        from the user in the bot's DMs.
    """

    __slots__ = ("user_id", "guild_id", "_state", "_cs_user", "_cs_guild")

    def __init__(self, data: dict[str, Any], state: ConnectionState):
        self._state = state
        # keys are Application Integration Types as strings
        self.user_id = int(uid) if (uid := data.get("1")) is not None else None
        self.guild_id = (
            int(guild_id) if (guild_id := data.get("0", None)) is not None else None
        )

    def __repr__(self):
        return f"<AuthorizingIntegrationOwners user_id={self.user_id} guild_id={self.guild_id}>"

    def __eq__(self, other):
        return (
            isinstance(other, AuthorizingIntegrationOwners)
            and self.user_id == other.user_id
            and self.guild_id == other.guild_id
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @utils.cached_slot_property("_cs_user")
    def user(self) -> User | None:
        """Optional[:class:`User`]: The user that authorized the integration.
        Returns ``None`` if the user is not in cache, or if :attr:`user_id` is ``None``.
        """
        if not self.user_id:
            return None
        return self._state.get_user(self.user_id)

    @utils.cached_slot_property("_cs_guild")
    def guild(self) -> Guild | None:
        """Optional[:class:`Guild`]: The guild that authorized the integration.
        Returns ``None`` if the guild is not in cache, or if :attr:`guild_id` is ``0`` or ``None``.
        """
        if not self.guild_id:
            return None
        return self._state._get_guild(self.guild_id)
