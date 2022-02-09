# -*- coding: utf-8 -*-

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
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple, Union

from . import utils
from .enums import try_enum, InteractionType, InteractionResponseType
from .errors import InteractionResponded, ClientException, InvalidArgument
from .channel import ChannelType, PartialMessageable
from .file import File
from .user import User
from .member import Member
from .message import Message, Attachment
from .object import Object
from .permissions import Permissions
from .webhook.async_ import async_context, Webhook, handle_message_parameters

__all__ = (
    'Interaction',
    'InteractionMessage',
    'InteractionResponse',
    'MessageInteraction',
)

if TYPE_CHECKING:
    from .types.interactions import (
        Interaction as InteractionPayload,
        InteractionData,
        MessageInteraction as MessageInteractionPayload
    )
    from .guild import Guild
    from .state import ConnectionState
    from .mentions import AllowedMentions
    from aiohttp import ClientSession
    from .embeds import Embed
    from .ui.view import View
    from .channel import VoiceChannel, StageChannel, TextChannel, CategoryChannel, StoreChannel, PartialMessageable
    from .threads import Thread
    from .commands import OptionChoice

    InteractionChannel = Union[
        VoiceChannel, StageChannel, TextChannel, CategoryChannel, StoreChannel, Thread, PartialMessageable
    ]


MISSING: Any = utils.MISSING


class Interaction:
    """Represents a Discord interaction.

    An interaction happens when a user does an action that needs to
    be notified. Current examples are slash commands and components.

    .. versionadded:: 2.0

    Attributes
    -----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel_id: Optional[:class:`int`]
        The channel ID the interaction was sent from.
    application_id: :class:`int`
        The application ID that the interaction was for.
    user: Optional[Union[:class:`User`, :class:`Member`]]
        The user or member that sent the interaction.
    message: Optional[:class:`Message`]
        The message that sent this interaction.
    token: :class:`str`
        The token to continue the interaction. These are valid
        for 15 minutes.
    data: :class:`dict`
        The raw interaction data.
    locale: :class:`str`
        The users locale.
    guild_locale: :class:`str`
        The guilds preferred locale, if invoked in a guild.
    """

    __slots__: Tuple[str, ...] = (
        'id',
        'type',
        'guild_id',
        'channel_id',
        'data',
        'application_id',
        'message',
        'user',
        'locale',
        'guild_locale',
        'token',
        'version',
        '_permissions',
        '_state',
        '_session',
        '_original_message',
        '_cs_response',
        '_cs_followup',
        '_cs_channel',
    )

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        self._state: ConnectionState = state
        self._session: ClientSession = state.http._HTTPClient__session
        self._original_message: Optional[InteractionMessage] = None
        self._from_data(data)

    def _from_data(self, data: InteractionPayload):
        self.id: int = int(data['id'])
        self.type: InteractionType = try_enum(InteractionType, data['type'])
        self.data: Optional[InteractionData] = data.get('data')
        self.token: str = data['token']
        self.version: int = data['version']
        self.channel_id: Optional[int] = utils._get_as_snowflake(data, 'channel_id')
        self.guild_id: Optional[int] = utils._get_as_snowflake(data, 'guild_id')
        self.application_id: int = int(data['application_id'])
        self.locale: Optional[str] = data.get('locale')
        self.guild_locale: Optional[str] = data.get('guild_locale')

        self.message: Optional[Message]
        try:
            self.message = Message(state=self._state, channel=self.channel, data=data['message'])  # type: ignore
        except KeyError:
            self.message = None

        self.user: Optional[Union[User, Member]] = None
        self._permissions: int = 0

        # TODO: there's a potential data loss here
        if self.guild_id:
            guild = self.guild or Object(id=self.guild_id)
            try:
                member = data['member']  # type: ignore
            except KeyError:
                pass
            else:
                self.user = Member(state=self._state, guild=guild, data=member)  # type: ignore
                self._permissions = int(member.get('permissions', 0))
        else:
            try:
                self.user = User(state=self._state, data=data['user'])
            except KeyError:
                pass

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild the interaction was sent from."""
        return self._state and self._state._get_guild(self.guild_id)

    def is_command(self) -> bool:
        """:class:`bool`: Indicates whether the interaction is an application command."""
        return self.type == InteractionType.application_command

    def is_component(self) -> bool:
        """:class:`bool`: Indicates whether the interaction is a message component."""
        return self.type == InteractionType.component

    @utils.cached_slot_property('_cs_channel')
    def channel(self) -> Optional[InteractionChannel]:
        """Optional[Union[:class:`abc.GuildChannel`, :class:`PartialMessageable`, :class:`Thread`]]: The channel the interaction was sent from.

        Note that due to a Discord limitation, DM channels are not resolved since there is
        no data to complete them. These are :class:`PartialMessageable` instead.
        """
        guild = self.guild
        channel = guild and guild._resolve_channel(self.channel_id)
        if channel is None:
            if self.channel_id is not None:
                type = ChannelType.text if self.guild_id is not None else ChannelType.private
                return PartialMessageable(state=self._state, id=self.channel_id, type=type)
            return None
        return channel

    @property
    def permissions(self) -> Permissions:
        """:class:`Permissions`: The resolved permissions of the member in the channel, including overwrites.

        In a non-guild context where this doesn't apply, an empty permissions object is returned.
        """
        return Permissions(self._permissions)

    @utils.cached_slot_property('_cs_response')
    def response(self) -> InteractionResponse:
        """:class:`InteractionResponse`: Returns an object responsible for handling responding to the interaction.

        A response can only be done once. If secondary messages need to be sent, consider using :attr:`followup`
        instead.
        """
        return InteractionResponse(self)

    @utils.cached_slot_property('_cs_followup')
    def followup(self) -> Webhook:
        """:class:`Webhook`: Returns the follow up webhook for follow up interactions."""
        payload = {
            'id': self.application_id,
            'type': 3,
            'token': self.token,
        }
        return Webhook.from_state(data=payload, state=self._state)

    async def original_message(self) -> InteractionMessage:
        """|coro|

        Fetches the original interaction response message associated with the interaction.

        If the interaction response was :meth:`InteractionResponse.send_message` then this would
        return the message that was sent using that response. Otherwise, this would return
        the message that triggered the interaction.

        Repeated calls to this will return a cached value.

        Raises
        -------
        HTTPException
            Fetching the original response message failed.
        ClientException
            The channel for the message could not be resolved.

        Returns
        --------
        InteractionMessage
            The original interaction response message.
        """

        if self._original_message is not None:
            return self._original_message

        # TODO: fix later to not raise?
        channel = self.channel
        if channel is None:
            raise ClientException('Channel for message could not be resolved')

        adapter = async_context.get()
        data = await adapter.get_original_interaction_response(
            application_id=self.application_id,
            token=self.token,
            session=self._session,
        )
        state = _InteractionMessageState(self, self._state)
        message = InteractionMessage(state=state, channel=channel, data=data)  # type: ignore
        self._original_message = message
        return message

    async def edit_original_message(
        self,
        *,
        content: Optional[str] = MISSING,
        embeds: List[Embed] = MISSING,
        embed: Optional[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: List[Attachment] = MISSING,
        view: Optional[View] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
        delete_after: Optional[float] = None,
    ) -> InteractionMessage:
        """|coro|

        Edits the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.edit` in case
        you do not want to fetch the message and save an HTTP request.

        This method is also the only way to edit the original message if
        the message sent was ephemeral.

        Parameters
        ------------
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

        Raises
        -------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        --------
        :class:`InteractionMessage`
            The newly edited message.
        """

        previous_mentions: Optional[AllowedMentions] = self._state.allowed_mentions
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
        )
        adapter = async_context.get()
        data = await adapter.edit_original_interaction_response(
            self.application_id,
            self.token,
            session=self._session,
            payload=params.payload,
            multipart=params.multipart,
            files=params.files,
        )

        # The message channel types should always match
        message = InteractionMessage(state=self._state, channel=self.channel, data=data)  # type: ignore
        if view and not view.is_finished():
            self._state.store_view(view, message.id)

        if delete_after is not None:
            await self.delete_original_message(delay=delete_after)

        return message

    async def delete_original_message(self, *, delay: Optional[float] = None) -> None:
        """|coro|

        Deletes the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.delete` in case
        you do not want to fetch the message and save an HTTP request.

        Parameters
        -----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait before deleting the message.
            The waiting is done in the background and deletion failures are ignored.

        Raises
        -------
        HTTPException
            Deleting the message failed.
        Forbidden
            Deleted a message that is not yours.
        """
        adapter = async_context.get()
        func = adapter.delete_original_interaction_response(
            self.application_id,
            self.token,
            session=self._session,
        )

        if delay is not None:
            utils.delay_task(delay, func)
        else:
            await func


class InteractionResponse:
    """Represents a Discord interaction response.

    This type can be accessed through :attr:`Interaction.response`.

    .. versionadded:: 2.0
    """

    __slots__: Tuple[str, ...] = (
        '_responded',
        '_parent',
    )

    def __init__(self, parent: Interaction):
        self._parent: Interaction = parent
        self._responded: bool = False

    def is_done(self) -> bool:
        """:class:`bool`: Indicates whether an interaction response has been done before.

        An interaction can only be responded to once.
        """
        return self._responded

    async def defer(self, *, ephemeral: bool = False) -> None:
        """|coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        Parameters
        -----------
        ephemeral: :class:`bool`
            Indicates whether the deferred message will eventually be ephemeral.
            If ``True`` for interactions of type :attr:`InteractionType.component`, this will defer ephemerally.

        Raises
        -------
        HTTPException
            Deferring the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        defer_type: int = 0
        data: Optional[Dict[str, Any]] = None
        parent = self._parent
        if parent.type is InteractionType.component:
            if ephemeral:
                data = {'flags': 64}
                defer_type = InteractionResponseType.deferred_channel_message.value
            else:
                defer_type = InteractionResponseType.deferred_message_update.value
        elif parent.type is InteractionType.application_command:
            defer_type = InteractionResponseType.deferred_channel_message.value
            if ephemeral:
                data = {'flags': 64}

        if defer_type:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id, parent.token, session=parent._session, type=defer_type, data=data
            )
            self._responded = True

    async def pong(self) -> None:
        """|coro|

        Pongs the ping interaction.

        This should rarely be used.

        Raises
        -------
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
            await adapter.create_interaction_response(
                parent.id, parent.token, session=parent._session, type=InteractionResponseType.pong.value
            )
            self._responded = True

    async def send_message(
        self,
        content: Optional[Any] = None,
        *,
        embed: Embed = MISSING,
        embeds: List[Embed] = MISSING,
        view: View = MISSING,
        tts: bool = False,
        ephemeral: bool = False,
        allowed_mentions: AllowedMentions = None,
        file: File = None,
        files: List[File] = None,
        delete_after: float = None
    ) -> Interaction:
        """|coro|

        Responds to this interaction by sending a message.

        Parameters
        -----------
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
            If a view is sent with an ephemeral message and it has no timeout set then the timeout
            is set to 15 minutes.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent.
        file: :class:`File`
            The file to upload.
        files: :class:`List[File]`
            A list of files to upload. Must be a maximum of 10.
            
        Raises
        -------
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

        payload: Dict[str, Any] = {
            'tts': tts,
        }

        if embed is not MISSING and embeds is not MISSING:
            raise TypeError('cannot mix embed and embeds keyword arguments')

        if embed is not MISSING and embed is not None:
            embeds = [embed]

        if embeds:
            if len(embeds) > 10:
                raise ValueError('embeds cannot exceed maximum of 10 elements')
            payload['embeds'] = [e.to_dict() for e in embeds]

        if content is not None:
            payload['content'] = str(content)

        if ephemeral:
            payload['flags'] = 64

        if view is not MISSING and view is not None:
            payload['components'] = view.to_components()

        state = self._parent._state

        if allowed_mentions is not None:
            if state.allowed_mentions is not None:
                payload['allowed_mentions'] = state.allowed_mentions.merge(allowed_mentions).to_dict()
            else:
                payload['allowed_mentions'] = allowed_mentions.to_dict()
        else:
            payload['allowed_mentions'] = state.allowed_mentions and state.allowed_mentions.to_dict()

        if file is not None and files is not None:
            raise InvalidArgument('cannot pass both file and files parameter to send()')
        
        if file is not None:
            if not isinstance(file, File):
                raise InvalidArgument('file parameter must be File')
            else:
                files = [file]

        if files is not None:
            if len(files) > 10:
                raise InvalidArgument('files parameter must be a list of up to 10 elements')
            elif not all(isinstance(file, File) for file in files):
                raise InvalidArgument('files parameter must be a list of File')

        parent = self._parent
        adapter = async_context.get()
        try:
            await adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                type=InteractionResponseType.channel_message.value,
                data=payload,
                files=files
            )
        finally:
            if files:
                for file in files:
                    file.close()

        if view is not MISSING and view is not None:
            if ephemeral and view.timeout is None:
                view.timeout = 15 * 60.0

            self._parent._state.store_view(view)

        self._responded = True
        if delete_after is not None:
            await self._parent.delete_original_message(delay=delete_after)
        return self._parent

    async def edit_message(
        self,
        *,
        content: Optional[Any] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        attachments: List[Attachment] = MISSING,
        view: Optional[View] = MISSING,
        delete_after: Optional[float] = None
    ) -> None:
        """|coro|

        Responds to this interaction by editing the original message of
        a component interaction.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The new content to replace the message with. ``None`` removes the content.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
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

        Raises
        -------
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
        if parent.type is not InteractionType.component:
            return

        payload = {}
        if content is not MISSING:
            if content is None:
                payload['content'] = None
            else:
                payload['content'] = str(content)

        if embed is not MISSING and embeds is not MISSING:
            raise TypeError('cannot mix both embed and embeds keyword arguments')

        if embed is not MISSING:
            if embed is None:
                embeds = []
            else:
                embeds = [embed]

        if embeds is not MISSING:
            payload['embeds'] = [e.to_dict() for e in embeds]

        if attachments is not MISSING:
            payload['attachments'] = [a.to_dict() for a in attachments]

        if view is not MISSING:
            state.prevent_view_updates_for(message_id)
            if view is None:
                payload['components'] = []
            else:
                payload['components'] = view.to_components()
        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            type=InteractionResponseType.message_update.value,
            data=payload,
        )

        if view and not view.is_finished():
            state.store_view(view, message_id)

        self._responded = True
        if delete_after is not None:
            await self._parent.delete_original_message(delay=delete_after)

    async def send_autocomplete_result(
        self,
        *,
        choices: List[OptionChoice],
    ) -> None:
        """|coro|
        Responds to this interaction by sending the autocomplete choices.

        Parameters
        -----------
        choices: List[:class:`OptionChoice`]
            A list of choices.  

        Raises
        -------
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

        payload = {
            "choices": [c.to_dict() for c in choices]
        }

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            type=InteractionResponseType.auto_complete_result.value,
            data=payload,
        )

        self._responded = True
        
class _InteractionMessageState:
    __slots__ = ('_parent', '_interaction')

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
    the interaction response. To retrieve this object see :meth:`Interaction.original_message`.

    This inherits from :class:`discord.Message` with changes to
    :meth:`edit` and :meth:`delete` to work.

    .. versionadded:: 2.0
    """

    __slots__ = ()
    _state: _InteractionMessageState

    async def edit(
        self,
        content: Optional[str] = MISSING,
        embeds: List[Embed] = MISSING,
        embed: Optional[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: List[Attachment] = MISSING,
        view: Optional[View] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
        delete_after: Optional[float] = None,
    ) -> InteractionMessage:
        """|coro|

        Edits the message.

        Parameters
        ------------
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

        Raises
        -------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        ---------
        :class:`InteractionMessage`
            The newly edited message.
        """
        if attachments is MISSING:
            attachments = self.attachments or MISSING
        return await self._state._interaction.edit_original_message(
            content=content,
            embeds=embeds,
            embed=embed,
            file=file,
            files=files,
            attachments=attachments,
            view=view,
            allowed_mentions=allowed_mentions,
            delete_after=delete_after
        )

    async def delete(self, *, delay: Optional[float] = None) -> None:
        """|coro|

        Deletes the message.

        Parameters
        -----------
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
        await self._state._interaction.delete_original_message(delay=delay)


class MessageInteraction:
    """Represents a Discord message interaction.

    This is sent on the message object when the message is a response
    to an interaction without an existing message e.g. application command.

    .. versionadded:: 2.0

    .. note::
        Responses to message components do not include this property.

    Attributes
    -----------
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

    __slots__: Tuple[str, ...] = (
        'id',
        'type',
        'name',
        'user',
        'data',
        '_state'
    )

    def __init__(self, *, data: MessageInteractionPayload, state: ConnectionState):
        self._state = state
        self.data = data
        self.id: int = int(data['id'])
        self.type: InteractionType = data['type']
        self.name: str = data['name']
        self.user: User = self._state.store_user(data['user'])
