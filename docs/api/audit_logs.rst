.. currentmodule:: discord

.. _discord-api-audit-logs:

Audit Log Data
==============

Working with :meth:`Guild.audit_logs` is a complicated process with a lot of machinery
involved. The library attempts to make it easy to use and friendly. In order to accomplish
this goal, it must make use of a couple of data classes that aid in this goal.

.. attributetable:: AuditLogEntry

.. autoclass:: AuditLogEntry
    :members:

.. attributetable:: AuditLogChanges

.. class:: AuditLogChanges

    An audit log change set.

    .. attribute:: before

        The old value. The attribute has the type of :class:`AuditLogDiff`.

        Depending on the :class:`AuditLogActionCategory` retrieved by
        :attr:`~AuditLogEntry.category`\, the data retrieved by this
        attribute differs:

        +----------------------------------------+---------------------------------------------------+
        |                Category                |                    Description                    |
        +----------------------------------------+---------------------------------------------------+
        | :attr:`~AuditLogActionCategory.create` | All attributes are set to ``None``.               |
        +----------------------------------------+---------------------------------------------------+
        | :attr:`~AuditLogActionCategory.delete` | All attributes are set the value before deletion. |
        +----------------------------------------+---------------------------------------------------+
        | :attr:`~AuditLogActionCategory.update` | All attributes are set the value before updating. |
        +----------------------------------------+---------------------------------------------------+
        | ``None``                               | No attributes are set.                            |
        +----------------------------------------+---------------------------------------------------+

    .. attribute:: after

        The new value. The attribute has the type of :class:`AuditLogDiff`.

        Depending on the :class:`AuditLogActionCategory` retrieved by
        :attr:`~AuditLogEntry.category`\, the data retrieved by this
        attribute differs:

        +----------------------------------------+--------------------------------------------------+
        |                Category                |                   Description                    |
        +----------------------------------------+--------------------------------------------------+
        | :attr:`~AuditLogActionCategory.create` | All attributes are set to the created value      |
        +----------------------------------------+--------------------------------------------------+
        | :attr:`~AuditLogActionCategory.delete` | All attributes are set to ``None``               |
        +----------------------------------------+--------------------------------------------------+
        | :attr:`~AuditLogActionCategory.update` | All attributes are set the value after updating. |
        +----------------------------------------+--------------------------------------------------+
        | ``None``                               | No attributes are set.                           |
        +----------------------------------------+--------------------------------------------------+

.. attributetable:: AuditLogDiff

.. class:: AuditLogDiff

    Represents an audit log "change" object. A change object has dynamic
    attributes that depend on the type of action being done. Certain actions
    map to certain attributes being set.

    Note that accessing an attribute that does not match the specified action
    will lead to an attribute error.

    To get a list of attributes that have been set, you can iterate over
    them. To see a list of all possible attributes that could be set based
    on the action being done, check the documentation for :class:`AuditLogAction`,
    otherwise check the documentation below for all attributes that are possible.

    .. container:: operations

        .. describe:: iter(diff)

            Returns an iterator over (attribute, value) tuple of this diff.

    .. attribute:: name

        A name of something.

        :type: :class:`str`

    .. attribute:: icon

        A guild's icon. See also :attr:`Guild.icon`.

        :type: :class:`Asset`

    .. attribute:: splash

        The guild's invite splash. See also :attr:`Guild.splash`.

        :type: :class:`Asset`

    .. attribute:: discovery_splash

        The guild's discovery splash. See also :attr:`Guild.discovery_splash`.

        :type: :class:`Asset`

    .. attribute:: banner

        The guild's banner. See also :attr:`Guild.banner`.

        :type: :class:`Asset`

    .. attribute:: owner

        The guild's owner. See also :attr:`Guild.owner`

        :type: Union[:class:`Member`, :class:`User`]

    .. attribute:: afk_channel

        The guild's AFK channel.

        If this could not be found, then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.afk_channel`.

        :type: Union[:class:`VoiceChannel`, :class:`Object`]

    .. attribute:: system_channel

        The guild's system channel.

        If this could not be found, then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.system_channel`.

        :type: Union[:class:`TextChannel`, :class:`Object`]


    .. attribute:: rules_channel

        The guild's rules channel.

        If this could not be found then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.rules_channel`.

        :type: Union[:class:`TextChannel`, :class:`Object`]


    .. attribute:: public_updates_channel

        The guild's public updates channel.

        If this could not be found then it falls back to a :class:`Object`
        with the ID being set.

        See :attr:`Guild.public_updates_channel`.

        :type: Union[:class:`TextChannel`, :class:`Object`]

    .. attribute:: afk_timeout

        The guild's AFK timeout. See :attr:`Guild.afk_timeout`.

        :type: :class:`int`

    .. attribute:: mfa_level

        The guild's MFA level. See :attr:`Guild.mfa_level`.

        :type: :class:`int`

    .. attribute:: widget_enabled

        The guild's widget has been enabled or disabled.

        :type: :class:`bool`

    .. attribute:: widget_channel

        The widget's channel.

        If this could not be found then it falls back to a :class:`Object`
        with the ID being set.

        :type: Union[:class:`TextChannel`, :class:`Object`]

    .. attribute:: verification_level

        The guild's verification level.

        See also :attr:`Guild.verification_level`.

        :type: :class:`VerificationLevel`

    .. attribute:: default_notifications

        The guild's default notification level.

        See also :attr:`Guild.default_notifications`.

        :type: :class:`NotificationLevel`

    .. attribute:: explicit_content_filter

        The guild's content filter.

        See also :attr:`Guild.explicit_content_filter`.

        :type: :class:`ContentFilter`

    .. attribute:: default_message_notifications

        The guild's default message notification setting.

        :type: :class:`int`

    .. attribute:: vanity_url_code

        The guild's vanity URL.

        See also :meth:`Guild.vanity_invite` and :meth:`Guild.edit`.

        :type: :class:`str`

    .. attribute:: position

        The position of a :class:`Role` or :class:`abc.GuildChannel`.

        :type: :class:`int`

    .. attribute:: type

        The type of channel or sticker.

        :type: Union[:class:`ChannelType`, :class:`StickerType`]

    .. attribute:: topic

        The topic of a :class:`TextChannel` or :class:`StageChannel`.

        See also :attr:`TextChannel.topic` or :attr:`StageChannel.topic`.

        :type: :class:`str`

    .. attribute:: bitrate

        The bitrate of a :class:`VoiceChannel`.

        See also :attr:`VoiceChannel.bitrate`.

        :type: :class:`int`

    .. attribute:: overwrites

        A list of permission overwrite tuples that represents a target and a
        :class:`PermissionOverwrite` for said target.

        The first element is the object being targeted, which can either
        be a :class:`Member` or :class:`User` or :class:`Role`. If this object
        is not found then it is a :class:`Object` with an ID being filled and
        a ``type`` attribute set to either ``'role'`` or ``'member'`` to help
        decide what type of ID it is.

        :type: List[Tuple[target, :class:`PermissionOverwrite`]]

    .. attribute:: privacy_level

        The privacy level of the stage instance or scheduled event.

        :type: Union[:class:`StagePrivacyLevel`, :class:`ScheduledEventPrivacyLevel`]

    .. attribute:: roles

        A list of roles being added or removed from a member.

        If a role is not found then it is a :class:`Object` with the ID and name being
        filled in.

        :type: List[Union[:class:`Role`, :class:`Object`]]

    .. attribute:: nick

        The nickname of a member.

        See also :attr:`Member.nick`

        :type: Optional[:class:`str`]

    .. attribute:: deaf

        Whether the member is being server deafened.

        See also :attr:`VoiceState.deaf`.

        :type: :class:`bool`

    .. attribute:: mute

        Whether the member is being server muted.

        See also :attr:`VoiceState.mute`.

        :type: :class:`bool`

    .. attribute:: permissions

        The permissions of a role.

        See also :attr:`Role.permissions`.

        :type: :class:`Permissions`

    .. attribute:: colour
                   color

        The colour of a role.

        See also :attr:`Role.colour`

        :type: :class:`Colour`

    .. attribute:: hoist

        Whether the role is being hoisted or not.

        See also :attr:`Role.hoist`

        :type: :class:`bool`

    .. attribute:: mentionable

        Whether the role is mentionable or not.

        See also :attr:`Role.mentionable`

        :type: :class:`bool`

    .. attribute:: code

        The invite's code.

        See also :attr:`Invite.code`

        :type: :class:`str`

    .. attribute:: channel

        A guild channel.

        If the channel is not found then it is a :class:`Object` with the ID
        being set. In some cases the channel name is also set.

        :type: Union[:class:`abc.GuildChannel`, :class:`Object`]

    .. attribute:: inviter

        The user who created the invite.

        See also :attr:`Invite.inviter`.

        :type: Optional[:class:`User`]

    .. attribute:: max_uses

        The invite's max uses.

        See also :attr:`Invite.max_uses`.

        :type: :class:`int`

    .. attribute:: uses

        The invite's current uses.

        See also :attr:`Invite.uses`.

        :type: :class:`int`

    .. attribute:: max_age

        The invite's max age in seconds.

        See also :attr:`Invite.max_age`.

        :type: :class:`int`

    .. attribute:: temporary

        If the invite is a temporary invite.

        See also :attr:`Invite.temporary`.

        :type: :class:`bool`

    .. attribute:: allow
                   deny

        The permissions being allowed or denied.

        :type: :class:`Permissions`

    .. attribute:: id

        The ID of the object being changed.

        :type: :class:`int`

    .. attribute:: avatar

        The avatar of a member.

        See also :attr:`User.avatar`.

        :type: :class:`Asset`

    .. attribute:: slowmode_delay

        The number of seconds members have to wait before
        sending another message in the channel.

        See also :attr:`TextChannel.slowmode_delay`.

        :type: :class:`int`

    .. attribute:: rtc_region

        The region for the voice channel’s voice communication.
        A value of ``None`` indicates automatic voice region detection.

        See also :attr:`VoiceChannel.rtc_region`.

        :type: :class:`VoiceRegion`

    .. attribute:: video_quality_mode

        The camera video quality for the voice channel's participants.

        See also :attr:`VoiceChannel.video_quality_mode`.

        :type: :class:`VideoQualityMode`

    .. attribute:: format_type

        The format type of a sticker being changed.

        See also :attr:`GuildSticker.format`

        :type: :class:`StickerFormatType`

    .. attribute:: emoji

        The name of the emoji that represents a sticker being changed.

        See also :attr:`GuildSticker.emoji`

        :type: :class:`str`

    .. attribute:: description

        The description of a sticker being changed.

        See also :attr:`GuildSticker.description`

        :type: :class:`str`

    .. attribute:: available

        The availability of a sticker being changed.

        See also :attr:`GuildSticker.available`

        :type: :class:`bool`

    .. attribute:: archived

        The thread is now archived.

        :type: :class:`bool`

    .. attribute:: locked

        The thread is being locked or unlocked.

        :type: :class:`bool`

    .. attribute:: auto_archive_duration

        The thread's auto archive duration being changed.

        See also :attr:`Thread.auto_archive_duration`

        :type: :class:`int`

    .. attribute:: default_auto_archive_duration

        The default auto archive duration for newly created threads being changed.

        :type: :class:`int`

    .. attribute:: invitable

        Non-moderators can now add other non-moderators to this thread.

        :type: :class:`bool`

    .. attribute:: command_id

        This command's permissions were updated.

        :type: :class:`int`

    .. attribute:: status

        The voice channel status of a :class:`VoiceChannel`.

        See also :attr:`VoiceChannel.status`.

        :type: :class:`str`

    .. attribute:: image

        The cover image of a :class:`ScheduledEvent`.

        :type: :class:`str`

    .. attribute:: communication_disabled_until

        Until when a :class:`Member` will be timed out

        :type: :class:`datetime.datetime` | :data:`None`

.. this is currently missing the following keys: reason and application_id
   I'm not sure how to about porting these
