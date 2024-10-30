.. currentmodule:: discord

.. _discord-api-events:

Event Reference
===============

This section outlines the different types of events listened by :class:`Client`.

There are 3 ways to register an event, the first way is through the use of
:meth:`Client.event`. The second way is through subclassing :class:`Client` and
overriding the specific events. The third way is through the use of :meth:`Client.listen`,
which can be used to assign multiple event handlers instead of only one like in :meth:`Client.event`.
For example:

.. code-block:: python
    :emphasize-lines: 17, 22

    import discord

    class MyClient(discord.Client):
        async def on_message(self, message):
            if message.author == self.user:
                return

            if message.content.startswith('$hello'):
                await message.channel.send('Hello World!')


    intents = discord.Intents.default()
    intents.message_content = True # Needed to see message content
    client = MyClient(intents=intents)

    # Overrides the 'on_message' method defined in MyClient
    @client.event
    async def on_message(message: discord.Message):
        print(f"Received {message.content}")

    # Assigns an ADDITIONAL handler
    @client.listen()
    async def on_message(message: discord.Message):
        print(f"Received {message.content}")

    # Runs only for the 1st event dispatch. Can be useful for listening to 'on_ready'
    @client.listen(once=True)
    async def on_ready():
        print("Client is ready!")


If an event handler raises an exception, :func:`on_error` will be called
to handle it, which defaults to print a traceback and ignoring the exception.

.. warning::

    All the events must be a |coroutine_link|_. If they aren't, then you might get unexpected
    errors. In order to turn a function into a coroutine they must be ``async def``
    functions.

Application Commands
--------------------
.. function:: on_application_command(context)

    Called when an application command is received.

    .. versionadded:: 2.0

    :param context: The ApplicationContext associated to the command being received.
    :type context: :class:`ApplicationContext`

.. function:: on_application_command_completion(context)

    Called when an application command is completed, after any checks have finished.

    .. versionadded:: 2.0

    :param context: The ApplicationContext associated to the command that was completed.
    :type context: :class:`ApplicationContext`

.. function:: on_application_command_error(context, exception)

    Called when an application command has an error.

    .. versionadded:: 2.0

    :param context: The ApplicationContext associated to the command that has an error.
    :type context: :class:`ApplicationContext`

    :param exception: The DiscordException associated to the error.
    :type exception: :class:`DiscordException`

.. function:: on_unknown_application_command(interaction)

    Called when an application command was not found in the bot's internal cache.

    .. versionadded:: 2.0

    :param interaction: The interaction associated to the unknown command.
    :type interaction: :class:`Interaction`

Audit Logs
----------

.. function:: on_audit_log_entry(entry)

    Called when an audit log entry is created.

    The bot must have :attr:`~Permissions.view_audit_log` to receive this, and
    :attr:`Intents.moderation` must be enabled.

    .. versionadded:: 2.5

    :param entry: The audit log entry that was created.
    :type entry: :class:`AuditLogEntry`

.. function:: on_raw_audit_log_entry(payload)

    Called when an audit log entry is created. Unlike
    :func:`on_audit_log_entry`, this is called regardless of the state of the internal
    user cache.

    The bot must have :attr:`~Permissions.view_audit_log` to receive this, and
    :attr:`Intents.moderation` must be enabled.

    .. versionadded:: 2.5

    :param payload: The raw event payload data.
    :type payload: :class:`RawAuditLogEntryEvent`

AutoMod
-------
.. function:: on_auto_moderation_rule_create(rule)

    Called when an auto moderation rule is created.

    The bot must have :attr:`~Permissions.manage_guild` to receive this, and
    :attr:`Intents.auto_moderation_configuration` must be enabled.

    :param rule: The newly created rule.
    :type rule: :class:`AutoModRule`

.. function:: on_auto_moderation_rule_update(rule)

    Called when an auto moderation rule is updated.

    The bot must have :attr:`~Permissions.manage_guild` to receive this, and
    :attr:`Intents.auto_moderation_configuration` must be enabled.

    :param rule: The updated rule.
    :type rule: :class:`AutoModRule`

.. function:: on_auto_moderation_rule_delete(rule)

    Called when an auto moderation rule is deleted.

    The bot must have :attr:`~Permissions.manage_guild` to receive this, and
    :attr:`Intents.auto_moderation_configuration` must be enabled.

    :param rule: The deleted rule.
    :type rule: :class:`AutoModRule`

.. function:: on_auto_moderation_action_execution(payload)

    Called when an auto moderation action is executed.

    The bot must have :attr:`~Permissions.manage_guild` to receive this, and
    :attr:`Intents.auto_moderation_execution` must be enabled.

    :param payload: The event's data.
    :type payload: :class:`AutoModActionExecutionEvent`

Bans
----
.. function:: on_member_ban(guild, user)

    Called when user gets banned from a :class:`Guild`.

    This requires :attr:`Intents.moderation` to be enabled.

    :param guild: The guild the user got banned from.
    :type guild: :class:`Guild`
    :param user: The user that got banned.
                 Can be either :class:`User` or :class:`Member` depending if
                 the user was in the guild or not at the time of removal.
    :type user: Union[:class:`User`, :class:`Member`]

.. function:: on_member_unban(guild, user)

    Called when a :class:`User` gets unbanned from a :class:`Guild`.

    This requires :attr:`Intents.moderation` to be enabled.

    :param guild: The guild the user got unbanned from.
    :type guild: :class:`Guild`
    :param user: The user that got unbanned.
    :type user: :class:`User`

Channels
--------
.. function:: on_private_channel_update(before, after)

    Called whenever a private group DM is updated. e.g. changed name or topic.

    This requires :attr:`Intents.messages` to be enabled.

    :param before: The updated group channel's old info.
    :type before: :class:`GroupChannel`
    :param after: The updated group channel's new info.
    :type after: :class:`GroupChannel`

.. function:: on_private_channel_pins_update(channel, last_pin)

    Called whenever a message is pinned or unpinned from a private channel.

    :param channel: The private channel that had its pins updated.
    :type channel: :class:`abc.PrivateChannel`
    :param last_pin: The latest message that was pinned as an aware datetime in UTC. Could be ``None``.
    :type last_pin: Optional[:class:`datetime.datetime`]

.. function:: on_guild_channel_update(before, after)

    Called whenever a guild channel is updated. e.g. changed name, topic, permissions.

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The updated guild channel's old info.
    :type before: :class:`abc.GuildChannel`
    :param after: The updated guild channel's new info.
    :type after: :class:`abc.GuildChannel`

.. function:: on_guild_channel_pins_update(channel, last_pin)

    Called whenever a message is pinned or unpinned from a guild channel.

    This requires :attr:`Intents.guilds` to be enabled.

    :param channel: The guild channel that had its pins updated.
    :type channel: Union[:class:`abc.GuildChannel`, :class:`Thread`]
    :param last_pin: The latest message that was pinned as an aware datetime in UTC. Could be ``None``.
    :type last_pin: Optional[:class:`datetime.datetime`]

.. function:: on_guild_channel_delete(channel)
              on_guild_channel_create(channel)

    Called whenever a guild channel is deleted or created.

    Note that you can get the guild from :attr:`~abc.GuildChannel.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    :param channel: The guild channel that got created or deleted.
    :type channel: :class:`abc.GuildChannel`

Connection
----------
.. function:: on_error(event, *args, **kwargs)

    Usually when an event raises an uncaught exception, a traceback is
    printed to stderr and the exception is ignored. If you want to
    change this behaviour and handle the exception for whatever reason
    yourself, this event can be overridden. Which, when done, will
    suppress the default action of printing the traceback.

    The information of the exception raised and the exception itself can
    be retrieved with a standard call to :func:`sys.exc_info`.

    If you want exception to propagate out of the :class:`Client` class
    you can define an ``on_error`` handler consisting of a single empty
    :ref:`raise statement <py:raise>`. Exceptions raised by ``on_error`` will not be
    handled in any way by :class:`Client`.

    .. note::

        ``on_error`` will only be dispatched to :meth:`Client.event`.

        It will not be received by :meth:`Client.wait_for`, or, if used,
        :ref:`ext_commands_api_bot` listeners such as
        :meth:`~ext.commands.Bot.listen` or :meth:`~ext.commands.Cog.listener`.

    :param event: The name of the event that raised the exception.
    :type event: :class:`str`

    :param args: The positional arguments for the event that raised the
        exception.
    :param kwargs: The keyword arguments for the event that raised the
        exception.

.. function:: on_connect()

    Called when the client has successfully connected to Discord. This is not
    the same as the client being fully prepared, see :func:`on_ready` for that.

    The warnings on :func:`on_ready` also apply.

    .. warning::

        Overriding this event will not call :meth:`Bot.sync_commands`.
        As a result, :class:`ApplicationCommand` will not be registered.

.. function:: on_shard_connect(shard_id)

    Similar to :func:`on_connect` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has connected to Discord.

    .. versionadded:: 1.4

    :param shard_id: The shard ID that has connected.
    :type shard_id: :class:`int`

.. function:: on_disconnect()

    Called when the client has disconnected from Discord, or a connection attempt to Discord has failed.
    This could happen either through the internet being disconnected, explicit calls to close,
    or Discord terminating the connection one way or the other.

    This function can be called many times without a corresponding :func:`on_connect` call.


.. function:: on_shard_disconnect(shard_id)

    Similar to :func:`on_disconnect` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has disconnected from Discord.

    .. versionadded:: 1.4

    :param shard_id: The shard ID that has disconnected.
    :type shard_id: :class:`int`

.. function:: on_ready()

    Called when the client is done preparing the data received from Discord. Usually after login is successful
    and the :attr:`Client.guilds` and co. are filled up.

    .. warning::

        This function is not guaranteed to be the first event called.
        Likewise, this function is **not** guaranteed to only be called
        once. This library implements reconnection logic and thus will
        end up calling this event whenever a RESUME request fails.

.. function:: on_shard_ready(shard_id)

    Similar to :func:`on_ready` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has become ready.

    :param shard_id: The shard ID that is ready.
    :type shard_id: :class:`int`

.. function:: on_resumed()

    Called when the client has resumed a session.

.. function:: on_shard_resumed(shard_id)

    Similar to :func:`on_resumed` except used by :class:`AutoShardedClient`
    to denote when a particular shard ID has resumed a session.

    .. versionadded:: 1.4

    :param shard_id: The shard ID that has resumed.
    :type shard_id: :class:`int`

.. function:: on_socket_event_type(event_type)

    Called whenever a WebSocket event is received from the WebSocket.

    This is mainly useful for logging how many events you are receiving
    from the Discord gateway.

    .. versionadded:: 2.0

    :param event_type: The event type from Discord that is received, e.g. ``'READY'``.
    :type event_type: :class:`str`

.. function:: on_socket_raw_receive(msg)

    Called whenever a message is completely received from the WebSocket, before
    it's processed and parsed. This event is always dispatched when a
    complete message is received and the passed data is not parsed in any way.

    This is only really useful for grabbing the WebSocket stream and
    debugging purposes.

    This requires setting the ``enable_debug_events`` setting in the :class:`Client`.

    .. note::

        This is only for the messages received from the client
        WebSocket. The voice WebSocket will not trigger this event.

    :param msg: The message passed in from the WebSocket library.
    :type msg: :class:`str`

.. function:: on_socket_raw_send(payload)

    Called whenever a send operation is done on the WebSocket before the
    message is sent. The passed parameter is the message that is being
    sent to the WebSocket.

    This is only really useful for grabbing the WebSocket stream and
    debugging purposes.

    This requires setting the ``enable_debug_events`` setting in the :class:`Client`.

    .. note::

        This is only for the messages sent from the client
        WebSocket. The voice WebSocket will not trigger this event.

    :param payload: The message that is about to be passed on to the
                    WebSocket library. It can be :class:`bytes` to denote a binary
                    message or :class:`str` to denote a regular text message.

Guilds
------
.. function:: on_guild_join(guild)

    Called when a :class:`Guild` is either created by the :class:`Client` or when the
    :class:`Client` joins a guild.

    This requires :attr:`Intents.guilds` to be enabled.

    :param guild: The guild that was joined.
    :type guild: :class:`Guild`

.. function:: on_guild_remove(guild)

    Called when a :class:`Guild` is removed from the :class:`Client`.

    This happens through, but not limited to, these circumstances:

    - The client got banned.
    - The client got kicked.
    - The client left the guild.
    - The client or the guild owner deleted the guild.

    In order for this event to be invoked then the :class:`Client` must have
    been part of the guild to begin with. (i.e. it is part of :attr:`Client.guilds`)

    This requires :attr:`Intents.guilds` to be enabled.

    :param guild: The guild that got removed.
    :type guild: :class:`Guild`

.. function:: on_guild_update(before, after)

    Called when a :class:`Guild` is updated, for example:

    - Changed name
    - Changed AFK channel
    - Changed AFK timeout
    - etc.

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The guild prior to being updated.
    :type before: :class:`Guild`
    :param after: The guild after being updated.
    :type after: :class:`Guild`

.. function:: on_guild_role_create(role)
              on_guild_role_delete(role)

    Called when a :class:`Guild` creates or deletes a :class:`Role`.

    To get the guild it belongs to, use :attr:`Role.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    :param role: The role that was created or deleted.
    :type role: :class:`Role`

.. function:: on_guild_role_update(before, after)

    Called when a :class:`Role` is changed guild-wide.

    This requires :attr:`Intents.guilds` to be enabled.

    :param before: The updated role's old info.
    :type before: :class:`Role`
    :param after: The updated role's updated info.
    :type after: :class:`Role`

.. function:: on_guild_emojis_update(guild, before, after)

    Called when a :class:`Guild` adds or removes an :class:`GuildEmoji`.

    This requires :attr:`Intents.emojis_and_stickers` to be enabled.

    :param guild: The guild who got their emojis updated.
    :type guild: :class:`Guild`
    :param before: A list of emojis before the update.
    :type before: Sequence[:class:`GuildEmoji`]
    :param after: A list of emojis after the update.
    :type after: Sequence[:class:`GuildEmoji`]

.. function:: on_guild_stickers_update(guild, before, after)

    Called when a :class:`Guild` adds or removes a sticker.

    This requires :attr:`Intents.emojis_and_stickers` to be enabled.

    .. versionadded:: 2.0

    :param guild: The guild who got their stickers updated.
    :type guild: :class:`Guild`
    :param before: A list of stickers before the update.
    :type before: Sequence[:class:`GuildSticker`]
    :param after: A list of stickers after the update.
    :type after: Sequence[:class:`GuildSticker`]

.. function:: on_guild_available(guild)
              on_guild_unavailable(guild)

    Called when a guild becomes available or unavailable. The guild must have
    existed in the :attr:`Client.guilds` cache.

    This requires :attr:`Intents.guilds` to be enabled.

    :param guild: The guild that has changed availability.
    :type guild: :class:`Guild`

.. function:: on_webhooks_update(channel)

    Called whenever a webhook is created, modified, or removed from a guild channel.

    This requires :attr:`Intents.webhooks` to be enabled.

    :param channel: The channel that had its webhooks updated.
    :type channel: :class:`abc.GuildChannel`

Integrations
------------
.. function:: on_guild_integrations_update(guild)

    Called whenever an integration is created, modified, or removed from a guild.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 1.4

    :param guild: The guild that had its integrations updated.
    :type guild: :class:`Guild`

.. function:: on_integration_create(integration)

    Called when an integration is created.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param integration: The integration that was created.
    :type integration: :class:`Integration`

.. function:: on_integration_update(integration)

    Called when an integration is updated.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param integration: The integration that was created.
    :type integration: :class:`Integration`

.. function:: on_raw_integration_delete(payload)

    Called when an integration is deleted.

    This requires :attr:`Intents.integrations` to be enabled.

    .. versionadded:: 2.0

    :param payload: The raw event payload data.
    :type payload: :class:`RawIntegrationDeleteEvent`

Interactions
------------
.. function:: on_interaction(interaction)

    Called when an interaction happened.

    This currently happens due to application command invocations or components being used.

    .. warning::

        This is a low level function that is not generally meant to be used.
        If you are working with components, consider using the callbacks associated
        with the :class:`~discord.ui.View` instead as it provides a nicer user experience.

    .. versionadded:: 2.0

    :param interaction: The interaction data.
    :type interaction: :class:`Interaction`

Invites
-------
.. function:: on_invite_create(invite)

    Called when an :class:`Invite` is created.
    You must have the :attr:`~Permissions.manage_channels` permission to receive this.

    .. versionadded:: 1.3

    .. note::

        There is a rare possibility that the :attr:`Invite.guild` and :attr:`Invite.channel`
        attributes will be of :class:`Object` rather than the respective models.

    This requires :attr:`Intents.invites` to be enabled.

    :param invite: The invite that was created.
    :type invite: :class:`Invite`

.. function:: on_invite_delete(invite)

    Called when an :class:`Invite` is deleted.
    You must have the :attr:`~Permissions.manage_channels` permission to receive this.

    .. versionadded:: 1.3

    .. note::

        There is a rare possibility that the :attr:`Invite.guild` and :attr:`Invite.channel`
        attributes will be of :class:`Object` rather than the respective models.

        Outside of those two attributes, the only other attribute guaranteed to be
        filled by the Discord gateway for this event is :attr:`Invite.code`.

    This requires :attr:`Intents.invites` to be enabled.

    :param invite: The invite that was deleted.
    :type invite: :class:`Invite`

Members/Users
-------------
.. function:: on_member_join(member)

    Called when a :class:`Member` joins a :class:`Guild`.

    This requires :attr:`Intents.members` to be enabled.

    :param member: The member who joined.
    :type member: :class:`Member`

.. function:: on_member_remove(member)

    Called when a :class:`Member` leaves a :class:`Guild`.

    If the guild or member could not be found in the internal cache, this event will not
    be called. Alternatively, :func:`on_raw_member_remove` is called regardless of the
    internal cache.

    This requires :attr:`Intents.members` to be enabled.

    :param member: The member who left.
    :type member: :class:`Member`

.. function:: on_raw_member_remove(payload)

    Called when a :class:`Member` leaves a :class:`Guild`. Unlike
    :func:`on_member_remove`, this is called regardless of the state of the internal
    member cache.

    This requires :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.4

    :param payload: The raw event payload data.
    :type payload: :class:`RawMemberRemoveEvent`

.. function:: on_member_update(before, after)

    Called when a :class:`Member` updates their profile.

    This is called when one or more of the following things change:

    - nickname
    - roles
    - pending
    - communication_disabled_until
    - timed_out

    This requires :attr:`Intents.members` to be enabled.

    :param before: The updated member's old info.
    :type before: :class:`Member`
    :param after: The updated member's updated info.
    :type after: :class:`Member`

.. function:: on_presence_update(before, after)

    Called when a :class:`Member` updates their presence.

    This is called when one or more of the following things change:

    - status
    - activity

    This requires :attr:`Intents.presences` and :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.0

    :param before: The updated member's old info.
    :type before: :class:`Member`
    :param after: The updated member's updated info.
    :type after: :class:`Member`

.. function:: on_voice_state_update(member, before, after)

    Called when a :class:`Member` changes their :class:`VoiceState`.

    The following, but not limited to, examples illustrate when this event is called:

    - A member joins a voice or stage channel.
    - A member leaves a voice or stage channel.
    - A member is muted or deafened by their own accord.
    - A member is muted or deafened by a guild administrator.

    This requires :attr:`Intents.voice_states` to be enabled.

    :param member: The member whose voice states changed.
    :type member: :class:`Member`
    :param before: The voice state prior to the changes.
    :type before: :class:`VoiceState`
    :param after: The voice state after the changes.
    :type after: :class:`VoiceState`

.. function:: on_user_update(before, after)

    Called when a :class:`User` updates their profile.

    This is called when one or more of the following things change:

    - avatar
    - username
    - discriminator
    - global_name

    This requires :attr:`Intents.members` to be enabled.

    :param before: The updated user's old info.
    :type before: :class:`User`
    :param after: The updated user's updated info.
    :type after: :class:`User`

Messages
--------
.. function:: on_message(message)

    Called when a :class:`Message` is created and sent.

    This requires :attr:`Intents.messages` to be enabled.

    .. warning::

        Your bot's own messages and private messages are sent through this
        event. This can lead cases of 'recursion' depending on how your bot was
        programmed. If you want the bot to not reply to itself, consider
        checking the user IDs. Note that :class:`~ext.commands.Bot` does not
        have this problem.

    :param message: The current message.
    :type message: :class:`Message`

.. function:: on_message_delete(message)

    Called when a message is deleted. If the message is not found in the
    internal message cache, then this event will not be called.
    Messages might not be in cache if the message is too old
    or the client is participating in high traffic guilds.

    If this occurs increase the :class:`max_messages <Client>` parameter
    or use the :func:`on_raw_message_delete` event instead.

    This requires :attr:`Intents.messages` to be enabled.

    :param message: The deleted message.
    :type message: :class:`Message`

.. function:: on_bulk_message_delete(messages)

    Called when messages are bulk deleted. If none of the messages deleted
    are found in the internal message cache, then this event will not be called.
    If individual messages were not found in the internal message cache,
    this event will still be called, but the messages not found will not be included in
    the messages list. Messages might not be in cache if the message is too old
    or the client is participating in high traffic guilds.

    If this occurs increase the :class:`max_messages <Client>` parameter
    or use the :func:`on_raw_bulk_message_delete` event instead.

    This requires :attr:`Intents.messages` to be enabled.

    :param messages: The messages that have been deleted.
    :type messages: List[:class:`Message`]

.. function:: on_raw_message_delete(payload)

    Called when a message is deleted. Unlike :func:`on_message_delete`, this is
    called regardless of the message being in the internal message cache or not.

    If the message is found in the message cache,
    it can be accessed via :attr:`RawMessageDeleteEvent.cached_message`

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessageDeleteEvent`

.. function:: on_raw_bulk_message_delete(payload)

    Called when a bulk delete is triggered. Unlike :func:`on_bulk_message_delete`, this is
    called regardless of the messages being in the internal message cache or not.

    If the messages are found in the message cache,
    they can be accessed via :attr:`RawBulkMessageDeleteEvent.cached_messages`

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawBulkMessageDeleteEvent`

.. function:: on_message_edit(before, after)

    Called when a :class:`Message` receives an update event. If the message is not found
    in the internal message cache, then these events will not be called.
    Messages might not be in cache if the message is too old
    or the client is participating in high traffic guilds.

    If this occurs increase the :class:`max_messages <Client>` parameter
    or use the :func:`on_raw_message_edit` event instead.

    The following non-exhaustive cases trigger this event:

    - A message has been pinned or unpinned.
    - The message content has been changed.
    - The message has received an embed.

        - For performance reasons, the embed server does not do this in a "consistent" manner.

    - The message's embeds were suppressed or unsuppressed.
    - A call message has received an update to its participants or ending time.
    - A poll has ended and the results have been finalized.

    This requires :attr:`Intents.messages` to be enabled.

    :param before: The previous version of the message.
    :type before: :class:`Message`
    :param after: The current version of the message.
    :type after: :class:`Message`

.. function:: on_raw_message_edit(payload)

    Called when a message is edited. Unlike :func:`on_message_edit`, this is called
    regardless of the state of the internal message cache.

    If the message is found in the message cache,
    it can be accessed via :attr:`RawMessageUpdateEvent.cached_message`. The cached message represents
    the message before it has been edited. For example, if the content of a message is modified and
    triggers the :func:`on_raw_message_edit` coroutine, the :attr:`RawMessageUpdateEvent.cached_message`
    will return a :class:`Message` object that represents the message before the content was modified.

    Due to the inherently raw nature of this event, the data parameter coincides with
    the raw data given by the `gateway <https://discord.com/developers/docs/topics/gateway#message-update>`_.

    Since the data payload can be partial, care must be taken when accessing stuff in the dictionary.
    One example of a common case of partial data is when the ``'content'`` key is inaccessible. This
    denotes an "embed" only edit, which is an edit in which only the embeds are updated by the Discord
    embed server.

    This requires :attr:`Intents.messages` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessageUpdateEvent`

Polls
~~~~~~
.. function:: on_poll_vote_add(poll, user, answer)

    Called when a vote is cast on a poll. If multiple answers were selected, this fires multiple times.
    if the poll was not found in the internal poll cache, then this
    event will not be called. Consider using :func:`on_raw_poll_vote_add` instead.

    This requires :attr:`Intents.polls` to be enabled.

    :param poll: The current state of the poll.
    :type poll: :class:`Poll`
    :param user: The user who added the vote.
    :type user: Union[:class:`Member`, :class:`User`]
    :param answer: The answer that was voted.
    :type answer: :class:`PollAnswer`

.. function:: on_raw_poll_vote_add(payload)

    Called when a vote is cast on a poll. Unlike :func:`on_poll_vote_add`, this is
    called regardless of the state of the internal poll cache.

    This requires :attr:`Intents.polls` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessagePollVoteEvent`

.. function:: on_poll_vote_remove(message, user, answer)

    Called when a vote is removed from a poll. If multiple answers were removed, this fires multiple times.
    if the poll is not found in the internal poll cache, then this
    event will not be called. Consider using :func:`on_raw_poll_vote_remove` instead.

    This requires :attr:`Intents.polls` to be enabled.

    :param poll: The current state of the poll.
    :type poll: :class:`Poll`
    :param user: The user who removed the vote.
    :type user: Union[:class:`Member`, :class:`User`]
    :param answer: The answer that was voted.
    :type answer: :class:`PollAnswer`

.. function:: on_raw_poll_vote_remove(payload)

    Called when a vote is removed from a poll. Unlike :func:`on_poll_vote_remove`, this is
    called regardless of the state of the internal message cache.

    This requires :attr:`Intents.polls` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawMessagePollVoteEvent`

Reactions
~~~~~~~~~
.. function:: on_reaction_add(reaction, user)

    Called when a message has a reaction added to it. Similar to :func:`on_message_edit`,
    if the message is not found in the internal message cache, then this
    event will not be called. Consider using :func:`on_raw_reaction_add` instead.

    .. note::

        To get the :class:`Message` being reacted, access it via :attr:`Reaction.message`.

    This requires :attr:`Intents.reactions` to be enabled.

    .. note::

        This doesn't require :attr:`Intents.members` within a guild context,
        but due to Discord not providing updated user information in a direct message
        it's required for direct messages to receive this event.
        Consider using :func:`on_raw_reaction_add` if you need this and do not otherwise want
        to enable the members intent.

    :param reaction: The current state of the reaction.
    :type reaction: :class:`Reaction`
    :param user: The user who added the reaction.
    :type user: Union[:class:`Member`, :class:`User`]

.. function:: on_raw_reaction_add(payload)

    Called when a message has a reaction added. Unlike :func:`on_reaction_add`, this is
    called regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionActionEvent`

.. function:: on_reaction_remove(reaction, user)

    Called when a message has a reaction removed from it. Similar to on_message_edit,
    if the message is not found in the internal message cache, then this event
    will not be called.

    .. note::

        To get the message being reacted, access it via :attr:`Reaction.message`.

    This requires both :attr:`Intents.reactions` and :attr:`Intents.members` to be enabled.

    .. note::

        Consider using :func:`on_raw_reaction_remove` if you need this and do not want
        to enable the members intent.

    :param reaction: The current state of the reaction.
    :type reaction: :class:`Reaction`
    :param user: The user who added the reaction.
    :type user: Union[:class:`Member`, :class:`User`]

.. function:: on_raw_reaction_remove(payload)

    Called when a message has a reaction removed. Unlike :func:`on_reaction_remove`, this is
    called regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionActionEvent`

.. function:: on_reaction_clear(message, reactions)

    Called when a message has all its reactions removed from it. Similar to :func:`on_message_edit`,
    if the message is not found in the internal message cache, then this event
    will not be called. Consider using :func:`on_raw_reaction_clear` instead.

    This requires :attr:`Intents.reactions` to be enabled.

    :param message: The message that had its reactions cleared.
    :type message: :class:`Message`
    :param reactions: The reactions that were removed.
    :type reactions: List[:class:`Reaction`]

.. function:: on_raw_reaction_clear(payload)

    Called when a message has all its reactions removed. Unlike :func:`on_reaction_clear`,
    this is called regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionClearEvent`

.. function:: on_reaction_clear_emoji(reaction)

    Called when a message has a specific reaction removed from it. Similar to :func:`on_message_edit`,
    if the message is not found in the internal message cache, then this event
    will not be called. Consider using :func:`on_raw_reaction_clear_emoji` instead.

    This requires :attr:`Intents.reactions` to be enabled.

    .. versionadded:: 1.3

    :param reaction: The reaction that got cleared.
    :type reaction: :class:`Reaction`

.. function:: on_raw_reaction_clear_emoji(payload)

    Called when a message has a specific reaction removed from it. Unlike :func:`on_reaction_clear_emoji` this is called
    regardless of the state of the internal message cache.

    This requires :attr:`Intents.reactions` to be enabled.

    .. versionadded:: 1.3

    :param payload: The raw event payload data.
    :type payload: :class:`RawReactionClearEmojiEvent`

Monetization
------------
.. function:: on_entitlement_create(entitlement)

    Called when a user subscribes to an SKU.

    .. versionadded:: 2.5

    :param entitlement: The entitlement that was created as a result of the subscription.
    :type entitlement: :class:`Entitlement`

.. function:: on_entitlement_update(entitlement)

    Called when a user's subscription to an Entitlement is cancelled.

    .. versionadded:: 2.5

    .. note::

        Before October 1, 2024, this event was called when a user's subscription was renewed.

        Entitlements that no longer follow this behavior will have a type of :attr:`EntitlementType.purchase`.
        Those that follow the old behavior will have a type of :attr:`EntitlementType.application_subscription`.

        `See the Discord changelog. <https://discord.com/developers/docs/change-log#premium-apps-entitlement-migration-and-new-subscription-api>`_

    :param entitlement: The entitlement that was updated.
    :type entitlement: :class:`Entitlement`

.. function:: on_entitlement_delete(entitlement)

    Called when a user's entitlement is deleted.

    Entitlements are usually only deleted when Discord issues a refund for a subscription,
    or manually removes an entitlement from a user.

    .. note::

        This is not called when a user's subscription is cancelled.

    .. versionadded:: 2.5

    :param entitlement: The entitlement that was deleted.
    :type entitlement: :class:`Entitlement`

.. function:: on_subscription_create(subscription)

    Called when a subscription is created for the application.

    .. versionadded:: 2.7

    :param subscription: The subscription that was created.
    :type subscription: :class:`Subscription`

.. function:: on_subscription_update(subscription)

    Called when a subscription has been updated. This could be a renewal, cancellation, or other payment related update.

    .. versionadded:: 2.7

    :param subscription: The subscription that was updated.
    :type subscription: :class:`Subscription`

.. function:: on_subscription_delete(subscription)

    Called when a subscription has been deleted.

    .. versionadded:: 2.7

    :param subscription: The subscription that was deleted.
    :type subscription: :class:`Subscription`

Scheduled Events
----------------
.. function:: on_scheduled_event_create(event)

    Called when an :class:`ScheduledEvent` is created.

    This requires :attr:`Intents.scheduled_events` to be enabled.

    :param event: The newly created scheduled event.
    :type event: :class:`ScheduledEvent`

.. function:: on_scheduled_event_update(before, after)

    Called when a scheduled event is updated.

    This requires :attr:`Intents.scheduled_events` to be enabled.

    :param before: The old scheduled event.
    :type before: :class:`ScheduledEvent`
    :param after: The updated scheduled event.
    :type after: :class:`ScheduledEvent`

.. function:: on_scheduled_event_delete(event)

    Called when a scheduled event is deleted.

    This requires :attr:`Intents.scheduled_events` to be enabled.

    :param event: The deleted scheduled event.
    :type event: :class:`ScheduledEvent`

.. function:: on_scheduled_event_user_add(event, member)

    Called when a user subscribes to an event. If the member or event
    is not found in the internal cache, then this event will not be
    called. Consider using :func:`on_raw_scheduled_event_user_add` instead.

    This requires :attr:`Intents.scheduled_events` to be enabled.

    :param event: The scheduled event subscribed to.
    :type event: :class:`ScheduledEvent`
    :param member: The member who subscribed.
    :type member: :class:`Member`

.. function:: on_raw_scheduled_event_user_add(payload)

    Called when a user subscribes to an event. Unlike
    :meth:`on_scheduled_event_user_add`, this will be called
    regardless of the state of the internal cache.

    This requires :attr:`Intents.scheduled_events` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawScheduledEventSubscription`

.. function:: on_scheduled_event_user_remove(event, member)

    Called when a user unsubscribes to an event. If the member or event is
    not found in the internal cache, then this event will not be called.
    Consider using :func:`on_raw_scheduled_event_user_remove` instead.

    This requires :attr:`Intents.scheduled_events` to be enabled.

    :param event: The scheduled event unsubscribed from.
    :type event: :class:`ScheduledEvent`
    :param member: The member who unsubscribed.
    :type member: :class:`Member`

.. function:: on_raw_scheduled_event_user_remove(payload)

    Called when a user unsubscribes to an event. Unlike
    :meth:`on_scheduled_event_user_remove`, this will be called
    regardless of the state of the internal cache.

    This requires :attr:`Intents.scheduled_events` to be enabled.

    :param payload: The raw event payload data.
    :type payload: :class:`RawScheduledEventSubscription`

Stage Instances
---------------
.. function:: on_stage_instance_create(stage_instance)
              on_stage_instance_delete(stage_instance)

    Called when a :class:`StageInstance` is created or deleted for a :class:`StageChannel`.

    .. versionadded:: 2.0

    :param stage_instance: The stage instance that was created or deleted.
    :type stage_instance: :class:`StageInstance`

.. function:: on_stage_instance_update(before, after)

    Called when a :class:`StageInstance` is updated.

    The following, but not limited to, examples illustrate when this event is called:

    - The topic is changed.
    - The privacy level is changed.

    .. versionadded:: 2.0

    :param before: The stage instance before the update.
    :type before: :class:`StageInstance`
    :param after: The stage instance after the update.
    :type after: :class:`StageInstance`

Threads
-------
.. function:: on_thread_join(thread)

    Called whenever a thread is joined.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.0

    :param thread: The thread that got joined.
    :type thread: :class:`Thread`

.. function:: on_thread_create(thread)

    Called whenever a thread is created.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.0

    :param thread: The thread that got created.
    :type thread: :class:`Thread`

.. function:: on_thread_remove(thread)

    Called whenever a thread is removed. This is different from a thread being deleted.

    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. warning::

        Due to technical limitations, this event might not be called
        as soon as one expects. Since the library tracks thread membership
        locally, the API only sends updated thread membership status upon being
        synced by joining a thread.

    .. versionadded:: 2.0

    :param thread: The thread that got removed.
    :type thread: :class:`Thread`

.. function:: on_thread_delete(thread)

    Called whenever a thread is deleted.  If the deleted thread isn't found in internal cache
    then this will not be called. Archived threads are not in the cache. Consider using :func:`on_raw_thread_delete`


    Note that you can get the guild from :attr:`Thread.guild`.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.0

    :param thread: The thread that got deleted.
    :type thread: :class:`Thread`

.. function:: on_raw_thread_delete(payload)

    Called whenever a thread is deleted. Unlike :func:`on_thread_delete` this is called
    regardless of the state of the internal cache.

    :param payload: The raw event payload data.
    :type payload: :class:`RawThreadDeleteEvent`

.. function:: on_thread_member_join(member)
              on_thread_member_remove(member)

    Called when a :class:`ThreadMember` leaves or joins a :class:`Thread`.

    You can get the thread a member belongs in by accessing :attr:`ThreadMember.thread`.

    This requires :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.0

    :param member: The member who joined or left.
    :type member: :class:`ThreadMember`


.. function:: on_raw_thread_member_remove(payload)

    Called when a :class:`ThreadMember` leaves a :class:`Thread`. Unlike :func:`on_thread_member_remove` this
    is called regardless of the member being in the thread's internal cache of members or not.

    This requires :attr:`Intents.members` to be enabled.

    .. versionadded:: 2.4

    :param payload: The raw event payload data.
    :type member: :class:`RawThreadMembersUpdateEvent`



.. function:: on_thread_update(before, after)

    Called whenever a thread is updated.

    This requires :attr:`Intents.guilds` to be enabled.

    If the thread could not be found in the internal cache, this event will not be called.
    Threads will not be in the cache if they are archived. Alternatively,
    :func:`on_raw_thread_update` is called regardless of the internal cache.

    .. versionadded:: 2.0

    :param before: The updated thread's old info.
    :type before: :class:`Thread`
    :param after: The updated thread's new info.
    :type after: :class:`Thread`


.. function:: on_raw_thread_update(payload)

    Called whenever a thread is updated.

    Unlike :func:`on_thread_update` this is called regardless of if the thread is in the
    internal thread cache or not.

    This requires :attr:`Intents.guilds` to be enabled.

    .. versionadded:: 2.4

    :param payload: The raw event payload data.
    :type payload: :class:`RawThreadUpdateEvent`

Typing
------
.. function:: on_typing(channel, user, when)

    Called when someone begins typing a message.

    The ``channel`` parameter can be a :class:`abc.Messageable` instance.
    Which could either be :class:`TextChannel`, :class:`GroupChannel`, or
    :class:`DMChannel`.

    If the ``channel`` is a :class:`TextChannel` then the ``user`` parameter
    is a :class:`Member`, otherwise it is a :class:`User`.

    This requires :attr:`Intents.typing` to be enabled.

    :param channel: The location where the typing originated from.
    :type channel: :class:`abc.Messageable`
    :param user: The user that started typing.
    :type user: Union[:class:`User`, :class:`Member`]
    :param when: When the typing started as an aware datetime in UTC.
    :type when: :class:`datetime.datetime`

.. function:: on_raw_typing(payload)

    Called when someone begins typing a message. Unlike :func:`on_typing`, this is
    called regardless if the user can be found in the bot's cache or not.

    If the typing event is occurring in a guild,
    the member that started typing can be accessed via :attr:`RawTypingEvent.member`

    This requires :attr:`Intents.typing` to be enabled.

    :param payload: The raw typing payload.
    :type payload: :class:`RawTypingEvent`


Voice Channel Status Update
---------------------------
.. function:: on_voice_channel_status_update(channel, before, after)

    Called when someone updates a voice channel status.

    .. versionadded:: 2.5

    :param channel: The channel where the voice channel status update originated from.
    :type channel: :class:`abc.GuildChannel`
    :param before: The old voice channel status.
    :type before: Optional[:class:`str`]
    :param after: The new voice channel status.
    :type after: Optional[:class:`str`]

.. function:: on_raw_voice_channel_status_update(payload)

    Called when someone updates a voice channels status.

    .. versionadded:: 2.5

    :param payload: The raw voice channel status update payload.
    :type payload: :class:`RawVoiceChannelStatusUpdateEvent`
