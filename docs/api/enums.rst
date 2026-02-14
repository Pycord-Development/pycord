.. currentmodule:: discord


.. _discord-api-enums:

Enumerations
============

The API provides some enumerations for certain types of strings to avoid the API
from being strongly typed in case the strings change in the future.

All enumerations are subclasses of an internal class which mimics the behaviour
of :class:`enum.Enum`.

.. class:: SlashCommandOptionType

    Specifies the input type of an option.

    .. versionadded:: 2.0

    .. attribute:: sub_command

        A slash subcommand.
    .. attribute:: sub_command_group

        A slash command group.
    .. attribute:: string

        A string.
    .. attribute:: integer

        An integer between -2⁵³ and 2⁵³.

        .. note::

            IDs, such as 881224361015672863, are often too big for this input type.

    .. attribute:: boolean

        A boolean.
    .. attribute:: user

        A user from the current channel. This will be converted to an instance of :class:`.User` in private channels, else :class:`.Member`
    .. attribute:: channel

        A channel from the current guild.
    .. attribute:: role

        A role from the current guild.
    .. attribute:: mentionable

        A mentionable (user or role).
    .. attribute:: number

        A floating-point number between -2⁵³ and 2⁵³.

        .. note::

            IDs, such as 881224361015672863, are often too big for this input type.

    .. attribute:: attachment

        An attachment.

.. class:: ChannelType

    Specifies the type of channel.

    .. attribute:: text

        A text channel.

    .. attribute:: voice

        A voice channel.

    .. attribute:: private

        A private text channel. Also called a direct message.

    .. attribute:: group

        A private group text channel.

    .. attribute:: category

        A category channel.

    .. attribute:: news

        A guild news channel.

    .. attribute:: stage_voice

        A guild stage voice channel.

        .. versionadded:: 1.7

    .. attribute:: news_thread

        A news thread.

        .. versionadded:: 2.0

    .. attribute:: public_thread

        A public thread.

        .. versionadded:: 2.0

    .. attribute:: private_thread

        A private thread.

        .. versionadded:: 2.0

    .. attribute:: directory

        A guild directory entry, used in hub guilds, currently in experiment.

        .. versionadded:: 2.0

    .. attribute:: forum

        User can only write in threads, similar functionality to a forum.

        .. versionadded:: 2.0

.. class:: MessageType

    Specifies the type of :class:`Message`. This is used to denote if a message
    is to be interpreted as a system message or a regular message.

    .. container:: operations

      .. describe:: x == y

          Checks if two messages are equal.
      .. describe:: x != y

          Checks if two messages are not equal.

    .. attribute:: default

        The default message type. This is the same as regular messages.
    .. attribute:: recipient_add

        The system message when a user is added to a group private
        message or a thread.
    .. attribute:: recipient_remove

        The system message when a user is removed from a group private
        message or a thread.
    .. attribute:: call

        The system message denoting call state, e.g. missed call, started call,
        etc.
    .. attribute:: channel_name_change

        The system message denoting that a channel's name has been changed.
    .. attribute:: channel_icon_change

        The system message denoting that a channel's icon has been changed.
    .. attribute:: pins_add

        The system message denoting that a pinned message has been added to a channel.
    .. attribute:: new_member

        The system message denoting that a new member has joined a Guild.

    .. attribute:: premium_guild_subscription

        The system message denoting that a member has "nitro boosted" a guild.
    .. attribute:: premium_guild_tier_1

        The system message denoting that a member has "nitro boosted" a guild
        and it achieved level 1.
    .. attribute:: premium_guild_tier_2

        The system message denoting that a member has "nitro boosted" a guild
        and it achieved level 2.
    .. attribute:: premium_guild_tier_3

        The system message denoting that a member has "nitro boosted" a guild
        and it achieved level 3.
    .. attribute:: channel_follow_add

        The system message denoting that an announcement channel has been followed.

        .. versionadded:: 1.3
    .. attribute:: guild_stream

        The system message denoting that a member is streaming in the guild.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_disqualified

        The system message denoting that the guild is no longer eligible for Server
        Discovery.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_requalified

        The system message denoting that the guild has become eligible again for Server
        Discovery.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_grace_period_initial_warning

        The system message denoting that the guild has failed to meet the Server
        Discovery requirements for one week.

        .. versionadded:: 1.7
    .. attribute:: guild_discovery_grace_period_final_warning

        The system message denoting that the guild has failed to meet the Server
        Discovery requirements for 3 weeks in a row.

        .. versionadded:: 1.7
    .. attribute:: thread_created

        The system message denoting that a thread has been created. This is only
        sent if the thread has been created from an older message. The period of time
        required for a message to be considered old cannot be relied upon and is up to
        Discord.

        .. versionadded:: 2.0
    .. attribute:: reply

        The system message denoting that the author is replying to a message.

        .. versionadded:: 2.0
    .. attribute:: application_command

        The system message denoting that an application (or "slash") command was executed.

        .. versionadded:: 2.0
    .. attribute:: guild_invite_reminder

        The system message sent as a reminder to invite people to the guild.

        .. versionadded:: 2.0
    .. attribute:: thread_starter_message

        The system message denoting the message in the thread that is the one that started the
        thread's conversation topic.

        .. versionadded:: 2.0
    .. attribute:: context_menu_command

        The system message denoting that an context menu command was executed.

        .. versionadded:: 2.0
    .. attribute:: auto_moderation_action

        The system message denoting an action by automod.

        .. versionadded:: 2.3
    .. attribute:: role_subscription_purchase

        The system message denoting a role-subscription purchase.

        .. versionadded:: 2.4

    .. attribute:: interaction_premium_upsell

        The system message denoting an interaction premium upsell.

        .. versionadded:: 2.4

    .. attribute:: stage_start

        The system message denoting that a stage event has started.

        .. versionadded:: 2.4

    .. attribute:: stage_end

        The system message denoting that a stage event has ended.

        .. versionadded:: 2.4

    .. attribute:: stage_speaker

        The system message denoting that a stage event has a new speaker.

        .. versionadded:: 2.4

    .. attribute:: stage_raise_hand

        The system message denoting that someone in a stage event is raising their hand.

        .. versionadded:: 2.4

    .. attribute:: stage_topic

        The system message denoting that a stage event has a new topic.

        .. versionadded:: 2.4

    .. attribute:: guild_application_premium_subscription

        The system message denoting that a member has subscribed to a guild application.

        .. versionadded:: 2.4

.. class:: UserFlags

    Represents Discord User flags.

    .. attribute:: staff

        The user is a Discord Employee.
    .. attribute:: partner

        The user is a Discord Partner.
    .. attribute:: hypesquad

        The user is a HypeSquad Events member.
    .. attribute:: bug_hunter

        The user is a Bug Hunter.
    .. attribute:: mfa_sms

        The user has SMS recovery for Multi Factor Authentication enabled.
    .. attribute:: premium_promo_dismissed

        The user has dismissed the Discord Nitro promotion.
    .. attribute:: hypesquad_bravery

        The user is a HypeSquad Bravery member.
    .. attribute:: hypesquad_brilliance

        The user is a HypeSquad Brilliance member.
    .. attribute:: hypesquad_balance

        The user is a HypeSquad Balance member.
    .. attribute:: early_supporter

        The user is an Early Supporter.
    .. attribute:: team_user

        The user is a Team User.
    .. attribute:: partner_or_verification_application

        Relates to partner/verification applications.
    .. attribute:: system

        The user is a system user (i.e. represents Discord officially).
    .. attribute:: has_unread_urgent_messages

        The user has an unread system message.
    .. attribute:: bug_hunter_level_2

        The user is a Bug Hunter Level 2.
    .. attribute:: underage_deleted

        The user was deleted for being underage.
    .. attribute:: verified_bot

        The user is a Verified Bot.
    .. attribute:: verified_bot_developer

        The user is an Early Verified Bot Developer.
    .. attribute:: discord_certified_moderator

        The user is a Moderator Programs Alumni.
    .. attribute:: bot_http_interactions

        The bot has set an interactions endpoint url.
    .. attribute:: spammer

        The user is disabled for being a spammer.
    .. attribute:: active_developer

        The user is an Active Developer.

.. class:: ActivityType

    Specifies the type of :class:`Activity`. This is used to check how to
    interpret the activity itself.

    .. attribute:: unknown

        An unknown activity type. This should generally not happen.
    .. attribute:: playing

        A "Playing" activity type.
    .. attribute:: streaming

        A "Streaming" activity type.
    .. attribute:: listening

        A "Listening" activity type.
    .. attribute:: watching

        A "Watching" activity type.
    .. attribute:: custom

        A custom activity type.
    .. attribute:: competing

        A competing activity type.

        .. versionadded:: 1.5

.. class:: InteractionType

    Specifies the type of :class:`Interaction`.

    .. versionadded:: 2.0

    .. attribute:: ping

        Represents Discord pinging to see if the interaction response server is alive.
    .. attribute:: application_command

        Represents a slash command interaction.
    .. attribute:: component

        Represents a component-based interaction, i.e. using the Discord Bot UI Kit.
    .. attribute:: auto_complete

        Represents a autocomplete interaction for slash commands.
    .. attribute:: modal_submit

        Represents a modal-based interaction.

.. class:: InteractionResponseType

    Specifies the response type for the interaction.

    .. versionadded:: 2.0

    .. attribute:: pong

        Pongs the interaction when given a ping.

        See also :meth:`InteractionResponse.pong`
    .. attribute:: channel_message

        Respond to the interaction with a message.

        See also :meth:`InteractionResponse.send_message`
    .. attribute:: deferred_channel_message

        Responds to the interaction with a message at a later time.

        See also :meth:`InteractionResponse.defer`
    .. attribute:: deferred_message_update

        Acknowledges the component interaction with a promise that
        the message will update later (though there is no need to actually update the message).

        See also :meth:`InteractionResponse.defer`
    .. attribute:: message_update

        Responds to the interaction by editing the message.

        See also :meth:`InteractionResponse.edit_message`
    .. attribute:: auto_complete_result

        Responds to the interaction by sending the autocomplete choices.

        See also :meth:`InteractionResponse.send_autocomplete_result`
    .. attribute:: modal

        Responds to the interaction by sending a modal dialog.

        See also :meth:`InteractionResponse.send_modal`

.. class:: ComponentType

    Represents the component type of a component.

    .. versionadded:: 2.0

    .. attribute:: action_row

        Represents the group component which holds different components in a row.
    .. attribute:: button

        Represents a button component.
    .. attribute:: select

        Represents a string select component.

        .. deprecated:: 2.3
            Use :attr:`ComponentType.string_select` instead.
    .. attribute:: string_select

        Represents a string select component.
    .. attribute:: input_text

        Represents an input_text component.
    .. attribute:: user_select

        Represents a user select component.
    .. attribute:: role_select

        Represents a role select component.
    .. attribute:: mentionable_select

        Represents a mentionable select component.
    .. attribute:: channel_select

        Represents a channel select component.
    .. attribute:: section

        Represents a section component.
    .. attribute:: text_display

        Represents a text display component.
    .. attribute:: thumbnail

        Represents a thumbnail component.
    .. attribute:: media_gallery

        Represents a media gallery component.
    .. attribute:: file

        Represents a file component.
    .. attribute:: separator

        Represents a separator component.
    .. attribute:: content_inventory_entry

        Represents a content inventory entry component.
    .. attribute:: container

        Represents a container component.
    .. attribute:: label

        Represents a label component.
    .. attribute:: file_upload

        Represents a file upload component.

.. class:: ButtonStyle

    Represents the style of the button component.

    .. versionadded:: 2.0

    .. attribute:: primary

        Represents a blurple button for the primary action.
    .. attribute:: secondary

        Represents a grey button for the secondary action.
    .. attribute:: success

        Represents a green button for a successful action.
    .. attribute:: danger

        Represents a red button for a dangerous action.
    .. attribute:: link

        Represents a link button.
    .. attribute:: premium

        Represents a premium button.

    .. attribute:: blurple

        An alias for :attr:`primary`.
    .. attribute:: grey

        An alias for :attr:`secondary`.
    .. attribute:: gray

        An alias for :attr:`secondary`.
    .. attribute:: green

        An alias for :attr:`success`.
    .. attribute:: red

        An alias for :attr:`danger`.
    .. attribute:: url

        An alias for :attr:`link`.

.. class:: InputTextStyle

    Represents the style of the input text component.

    .. versionadded:: 2.0

    .. attribute:: short

        Represents a single-line input text field.
    .. attribute:: long

        Represents a multi-line input text field.
    .. attribute:: singleline

        An alias for :attr:`short`.
    .. attribute:: multiline

        An alias for :attr:`long`.
    .. attribute:: paragraph

        An alias for :attr:`long`.

.. class:: VoiceRegion

    Specifies the region a voice server belongs to.

    .. attribute:: amsterdam

        The Amsterdam region.
    .. attribute:: brazil

        The Brazil region.
    .. attribute:: dubai

        The Dubai region.

        .. versionadded:: 1.3

    .. attribute:: eu_central

        The EU Central region.
    .. attribute:: eu_west

        The EU West region.
    .. attribute:: europe

        The Europe region.

        .. versionadded:: 1.3

    .. attribute:: frankfurt

        The Frankfurt region.
    .. attribute:: hongkong

        The Hong Kong region.
    .. attribute:: india

        The India region.

        .. versionadded:: 1.2

    .. attribute:: japan

        The Japan region.
    .. attribute:: london

        The London region.
    .. attribute:: russia

        The Russia region.
    .. attribute:: singapore

        The Singapore region.
    .. attribute:: southafrica

        The South Africa region.
    .. attribute:: south_korea

        The South Korea region.
    .. attribute:: sydney

        The Sydney region.
    .. attribute:: us_central

        The US Central region.
    .. attribute:: us_east

        The US East region.
    .. attribute:: us_south

        The US South region.
    .. attribute:: us_west

        The US West region.
    .. attribute:: vip_amsterdam

        The Amsterdam region for VIP guilds.
    .. attribute:: vip_us_east

        The US East region for VIP guilds.
    .. attribute:: vip_us_west

        The US West region for VIP guilds.

.. class:: VerificationLevel

    Specifies a :class:`Guild`\'s verification level, which is the criteria in
    which a member must meet before being able to send messages to the guild.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two verification levels are equal.
        .. describe:: x != y

            Checks if two verification levels are not equal.
        .. describe:: x > y

            Checks if a verification level is higher than another.
        .. describe:: x < y

            Checks if a verification level is lower than another.
        .. describe:: x >= y

            Checks if a verification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a verification level is lower or equal to another.

    .. attribute:: none

        No criteria set.
    .. attribute:: low

        Member must have a verified email on their Discord account.
    .. attribute:: medium

        Member must have a verified email and be registered on Discord for more
        than five minutes.
    .. attribute:: high

        Member must have a verified email, be registered on Discord for more
        than five minutes, and be a member of the guild itself for more than
        ten minutes.
    .. attribute:: highest

        Member must have a verified phone on their Discord account.

.. class:: NotificationLevel

    Specifies whether a :class:`Guild` has notifications on for all messages or mentions only by default.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two notification levels are equal.
        .. describe:: x != y

            Checks if two notification levels are not equal.
        .. describe:: x > y

            Checks if a notification level is higher than another.
        .. describe:: x < y

            Checks if a notification level is lower than another.
        .. describe:: x >= y

            Checks if a notification level is higher or equal to another.
        .. describe:: x <= y

            Checks if a notification level is lower or equal to another.

    .. attribute:: all_messages

        Members receive notifications for every message regardless of them being mentioned.
    .. attribute:: only_mentions

        Members receive notifications for messages they are mentioned in.

.. class:: ContentFilter

    Specifies a :class:`Guild`\'s explicit content filter, which is the machine
    learning algorithms that Discord uses to detect if an image contains
    pornography or otherwise explicit content.

    .. container:: operations

        .. versionadded:: 2.0

        .. describe:: x == y

            Checks if two content filter levels are equal.
        .. describe:: x != y

            Checks if two content filter levels are not equal.
        .. describe:: x > y

            Checks if a content filter level is higher than another.
        .. describe:: x < y

            Checks if a content filter level is lower than another.
        .. describe:: x >= y

            Checks if a content filter level is higher or equal to another.
        .. describe:: x <= y

            Checks if a content filter level is lower or equal to another.

    .. attribute:: disabled

        The guild does not have the content filter enabled.
    .. attribute:: no_role

        The guild has the content filter enabled for members without a role.
    .. attribute:: all_members

        The guild has the content filter enabled for every member.

.. class:: Status

    Specifies a :class:`Member` 's status.

    .. attribute:: online

        The member is online.
    .. attribute:: offline

        The member is offline.
    .. attribute:: idle

        The member is idle.
    .. attribute:: dnd

        The member is "Do Not Disturb".
    .. attribute:: do_not_disturb

        An alias for :attr:`dnd`.
    .. attribute:: invisible

        The member is "invisible". In reality, this is only used in sending
        a presence a la :meth:`Client.change_presence`. When you receive a
        user's presence this will be :attr:`offline` instead.
    .. attribute:: streaming

        The member is streaming.


.. class:: AuditLogAction

    Represents the type of action being done for a :class:`AuditLogEntry`\,
    which is retrievable via :meth:`Guild.audit_logs`.

    .. attribute:: guild_update

        The guild has updated. Things that trigger this include:

        - Changing the guild vanity URL
        - Changing the guild invite splash
        - Changing the guild AFK channel or timeout
        - Changing the guild voice server region
        - Changing the guild icon, banner, or discovery splash
        - Changing the guild moderation settings
        - Changing things related to the guild widget

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Guild`.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.afk_channel`
        - :attr:`~AuditLogDiff.system_channel`
        - :attr:`~AuditLogDiff.afk_timeout`
        - :attr:`~AuditLogDiff.default_message_notifications`
        - :attr:`~AuditLogDiff.explicit_content_filter`
        - :attr:`~AuditLogDiff.mfa_level`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.owner`
        - :attr:`~AuditLogDiff.splash`
        - :attr:`~AuditLogDiff.discovery_splash`
        - :attr:`~AuditLogDiff.icon`
        - :attr:`~AuditLogDiff.banner`
        - :attr:`~AuditLogDiff.vanity_url_code`

    .. attribute:: channel_create

        A new channel was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        either a :class:`abc.GuildChannel` or :class:`Object` with an ID.

        A more filled out object in the :class:`Object` case can be found
        by using :attr:`~AuditLogEntry.after`.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.overwrites`

    .. attribute:: channel_update

        A channel was updated. Things that trigger this include:

        - The channel name or topic was changed
        - The channel bitrate was changed

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`abc.GuildChannel` or :class:`Object` with an ID.

        A more filled out object in the :class:`Object` case can be found
        by using :attr:`~AuditLogEntry.after` or :attr:`~AuditLogEntry.before`.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.position`
        - :attr:`~AuditLogDiff.overwrites`
        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.bitrate`
        - :attr:`~AuditLogDiff.rtc_region`
        - :attr:`~AuditLogDiff.video_quality_mode`
        - :attr:`~AuditLogDiff.default_auto_archive_duration`

    .. attribute:: channel_delete

        A channel was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        an :class:`Object` with an ID.

        A more filled out object can be found by using the
        :attr:`~AuditLogEntry.before` object.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.overwrites`

    .. attribute:: overwrite_create

        A channel permission overwrite was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`abc.GuildChannel` or :class:`Object` with an ID.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        either a :class:`Role` or :class:`Member`. If the object is not found
        then it is a :class:`Object` with an ID being filled, a name, and a
        ``type`` attribute set to either ``'role'`` or ``'member'`` to help
        dictate what type of ID it is.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.deny`
        - :attr:`~AuditLogDiff.allow`
        - :attr:`~AuditLogDiff.id`
        - :attr:`~AuditLogDiff.type`

    .. attribute:: overwrite_update

        A channel permission overwrite was changed, this is typically
        when the permission values change.

        See :attr:`overwrite_create` for more information on how the
        :attr:`~AuditLogEntry.target` and :attr:`~AuditLogEntry.extra` fields
        are set.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.deny`
        - :attr:`~AuditLogDiff.allow`
        - :attr:`~AuditLogDiff.id`
        - :attr:`~AuditLogDiff.type`

    .. attribute:: overwrite_delete

        A channel permission overwrite was deleted.

        See :attr:`overwrite_create` for more information on how the
        :attr:`~AuditLogEntry.target` and :attr:`~AuditLogEntry.extra` fields
        are set.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.deny`
        - :attr:`~AuditLogDiff.allow`
        - :attr:`~AuditLogDiff.id`
        - :attr:`~AuditLogDiff.type`

    .. attribute:: kick

        A member was kicked.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`User` who got kicked.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: member_prune

        A member prune was triggered.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        set to ``None``.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``delete_members_days``: An integer specifying how far the prune was.
        - ``members_removed``: An integer specifying how many members were removed.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: ban

        A member was banned.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`User` who got banned.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: unban

        A member was unbanned.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`User` who got unbanned.

        When this is the action, :attr:`~AuditLogEntry.changes` is empty.

    .. attribute:: member_update

        A member has updated. This triggers in the following situations:

        - A nickname was changed
        - They were server muted or deafened (or it was undone)

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who got updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.nick`
        - :attr:`~AuditLogDiff.mute`
        - :attr:`~AuditLogDiff.deaf`

    .. attribute:: member_role_update

        A member's role has been updated. This triggers when a member
        either gains a role or loses a role.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who got the role.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.roles`

    .. attribute:: member_move

        A member's voice channel has been updated. This triggers when a
        member is moved to a different voice channel.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the members were moved.
        - ``count``: An integer specifying how many members were moved.

        .. versionadded:: 1.3

    .. attribute:: member_disconnect

        A member's voice state has changed. This triggers when a
        member is force disconnected from voice.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with one attribute:

        - ``count``: An integer specifying how many members were disconnected.

        .. versionadded:: 1.3

    .. attribute:: bot_add

        A bot was added to the guild.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` which was added to the guild.

        .. versionadded:: 1.3

    .. attribute:: role_create

        A new role was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Role` or a :class:`Object` with the ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.colour`
        - :attr:`~AuditLogDiff.mentionable`
        - :attr:`~AuditLogDiff.hoist`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.permissions`

    .. attribute:: role_update

        A role was updated. This triggers in the following situations:

        - The name has changed
        - The permissions have changed
        - The colour has changed
        - Its hoist/mentionable state has changed

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Role` or a :class:`Object` with the ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.colour`
        - :attr:`~AuditLogDiff.mentionable`
        - :attr:`~AuditLogDiff.hoist`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.permissions`

    .. attribute:: role_delete

        A role was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Role` or a :class:`Object` with the ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.colour`
        - :attr:`~AuditLogDiff.mentionable`
        - :attr:`~AuditLogDiff.hoist`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.permissions`

    .. attribute:: invite_create

        An invite was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Invite` that was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.max_age`
        - :attr:`~AuditLogDiff.code`
        - :attr:`~AuditLogDiff.temporary`
        - :attr:`~AuditLogDiff.inviter`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.uses`
        - :attr:`~AuditLogDiff.max_uses`

    .. attribute:: invite_update

        An invite was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Invite` that was updated.

    .. attribute:: invite_delete

        An invite was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Invite` that was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.max_age`
        - :attr:`~AuditLogDiff.code`
        - :attr:`~AuditLogDiff.temporary`
        - :attr:`~AuditLogDiff.inviter`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.uses`
        - :attr:`~AuditLogDiff.max_uses`

    .. attribute:: webhook_create

        A webhook was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the webhook ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type` (always set to ``1`` if so)

    .. attribute:: webhook_update

        A webhook was updated. This trigger in the following situations:

        - The webhook name changed
        - The webhook channel changed

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the webhook ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.avatar`

    .. attribute:: webhook_delete

        A webhook was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the webhook ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.type` (always set to ``1`` if so)

    .. attribute:: emoji_create

        An emoji was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildEmoji` or :class:`Object` with the emoji ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`

    .. attribute:: emoji_update

        An emoji was updated. This triggers when the name has changed.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildEmoji` or :class:`Object` with the emoji ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`

    .. attribute:: emoji_delete

        An emoji was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the emoji ID.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`

    .. attribute:: message_delete

        A message was deleted by a moderator. Note that this
        only triggers if the message was deleted by someone other than the author.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``count``: An integer specifying how many messages were deleted.
        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message got deleted.

    .. attribute:: message_bulk_delete

        Messages were bulk deleted by a moderator.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`TextChannel` or :class:`Object` with the ID of the channel that was purged.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with one attribute:

        - ``count``: An integer specifying how many messages were deleted.

        .. versionadded:: 1.3

    .. attribute:: message_pin

        A message was pinned in a channel.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message pinned.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message was pinned.
        - ``message_id``: the ID of the message which was pinned.

        .. versionadded:: 1.3

    .. attribute:: message_unpin

        A message was unpinned in a channel.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Member` or :class:`User` who had their message unpinned.

        When this is the action, the type of :attr:`~AuditLogEntry.extra` is
        set to an unspecified proxy object with two attributes:

        - ``channel``: A :class:`TextChannel` or :class:`Object` with the channel ID where the message was unpinned.
        - ``message_id``: the ID of the message which was unpinned.

        .. versionadded:: 1.3

    .. attribute:: integration_create

        A guild integration was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the integration ID of the integration which was created.

        .. versionadded:: 1.3

    .. attribute:: integration_update

        A guild integration was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the integration ID of the integration which was updated.

        .. versionadded:: 1.3

    .. attribute:: integration_delete

        A guild integration was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Object` with the integration ID of the integration which was deleted.

        .. versionadded:: 1.3

    .. attribute:: stage_instance_create

        A stage instance was started.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`StageInstance` or :class:`Object` with the ID of the stage
        instance which was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.privacy_level`

        .. versionadded:: 2.0

    .. attribute:: stage_instance_update

        A stage instance was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`StageInstance` or :class:`Object` with the ID of the stage
        instance which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.topic`
        - :attr:`~AuditLogDiff.privacy_level`

        .. versionadded:: 2.0

    .. attribute:: stage_instance_delete

        A stage instance was ended.

        .. versionadded:: 2.0

    .. attribute:: sticker_create

        A sticker was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
        which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.emoji`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.format_type`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.available`

        .. versionadded:: 2.0

    .. attribute:: sticker_update

        A sticker was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
        which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.emoji`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.format_type`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.available`

        .. versionadded:: 2.0

    .. attribute:: sticker_delete

        A sticker was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`GuildSticker` or :class:`Object` with the ID of the sticker
        which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.emoji`
        - :attr:`~AuditLogDiff.type`
        - :attr:`~AuditLogDiff.format_type`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.available`

        .. versionadded:: 2.0

    .. attribute:: scheduled_event_create

        A scheduled event was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`ScheduledEvent` or :class:`Object` with the ID of the thread which
        was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.privacy_level`
        - :attr:`~discord.ScheduledEvent.location`
        - :attr:`~discord.ScheduledEvent.status`
        - :attr:`~discord.ScheduledEventLocation.type`
        - :attr:`~discord.ScheduledEvent.image`

        .. versionadded:: 2.0

    .. attribute:: scheduled_event_update

        A scheduled event was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`ScheduledEvent` or :class:`Object` with the ID of the thread which
        was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.privacy_level`
        - :attr:`~discord.ScheduledEvent.location`
        - :attr:`~discord.ScheduledEvent.status`
        - :attr:`~discord.ScheduledEventLocation.type`
        - :attr:`~discord.ScheduledEvent.image`

        .. versionadded:: 2.0

    .. attribute:: scheduled_event_delete

        A scheduled event was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`ScheduledEvent` or :class:`Object` with the ID of the thread which
        was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.description`
        - :attr:`~AuditLogDiff.channel`
        - :attr:`~AuditLogDiff.privacy_level`
        - :attr:`~discord.ScheduledEvent.location`
        - :attr:`~discord.ScheduledEvent.status`
        - :attr:`~discord.ScheduledEventLocation.type`
        - :attr:`~discord.ScheduledEvent.image`

        .. versionadded:: 2.0

    .. attribute:: thread_create

        A thread was created.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Thread` or :class:`Object` with the ID of the thread which
        was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.archived`
        - :attr:`~AuditLogDiff.locked`
        - :attr:`~AuditLogDiff.auto_archive_duration`
        - :attr:`~AuditLogDiff.invitable`

        .. versionadded:: 2.0

    .. attribute:: thread_update

        A thread was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Thread` or :class:`Object` with the ID of the thread which
        was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.archived`
        - :attr:`~AuditLogDiff.locked`
        - :attr:`~AuditLogDiff.auto_archive_duration`
        - :attr:`~AuditLogDiff.invitable`

        .. versionadded:: 2.0

    .. attribute:: thread_delete

        A thread was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`Thread` or :class:`Object` with the ID of the thread which
        was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.archived`
        - :attr:`~AuditLogDiff.locked`
        - :attr:`~AuditLogDiff.auto_archive_duration`
        - :attr:`~AuditLogDiff.invitable`

        .. versionadded:: 2.0

    .. attribute:: application_command_permission_update

        An application command's permissions were updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        an :class:`Object` with the ID of the command that
        had it's permissions edited.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.command_id`

        .. versionadded:: 2.0

    .. attribute:: auto_moderation_rule_create

        A guild auto moderation rule was created.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.enabled`
        - :attr:`~AuditLogDiff.trigger_type`
        - :attr:`~AuditLogDiff.event_type`
        - :attr:`~AuditLogDiff.trigger_metadata`
        - :attr:`~AuditLogDiff.actions`
        - :attr:`~AuditLogDiff.exempt_roles`
        - :attr:`~AuditLogDiff.exempt_channels`

        .. versionadded:: 2.5

    .. attribute:: auto_moderation_rule_update

        A guild auto moderation rule was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.enabled`
        - :attr:`~AuditLogDiff.trigger_type`
        - :attr:`~AuditLogDiff.trigger_metadata`
        - :attr:`~AuditLogDiff.actions`
        - :attr:`~AuditLogDiff.exempt_roles`
        - :attr:`~AuditLogDiff.exempt_channels`

        .. versionadded:: 2.5

    .. attribute:: auto_moderation_rule_delete

        A guild auto moderation rule was deleted.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.name`
        - :attr:`~AuditLogDiff.enabled`
        - :attr:`~AuditLogDiff.trigger_type`
        - :attr:`~AuditLogDiff.event_type`
        - :attr:`~AuditLogDiff.trigger_metadata`
        - :attr:`~AuditLogDiff.actions`
        - :attr:`~AuditLogDiff.exempt_roles`
        - :attr:`~AuditLogDiff.exempt_channels`

        .. versionadded:: 2.5

    .. attribute:: auto_moderation_block_message

        A message was blocked by auto moderation.

        .. versionadded:: 2.5

    .. attribute:: auto_moderation_flag_to_channel

        A message was flagged by auto moderation.

        .. versionadded:: 2.5

    .. attribute:: auto_moderation_user_communication_disabled

        A member was timed out by auto moderation.

        .. versionadded:: 2.5

    .. attribute:: creator_monetization_request_created

        A creator monetization request was created.

        .. versionadded:: 2.5

    .. attribute:: creator_monetization_terms_accepted

        The creator monetization terms were accepted.

        .. versionadded:: 2.5

    .. attribute:: voice_channel_status_update

        A voice channel status was updated.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`VoiceChannel` or :class:`Object` with the ID of the voice
        channel which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.status`

        .. versionadded:: 2.5

    .. attribute:: voice_channel_status_delete

        A voice channel status was deleted.

        When this is the action, the type of :attr:`~AuditLogEntry.target` is
        the :class:`VoiceChannel` or :class:`Object` with the ID of the voice
        channel which was updated.

        Possible attributes for :class:`AuditLogDiff`:

        - :attr:`~AuditLogDiff.status`

        .. versionadded:: 2.5


.. class:: AuditLogActionCategory

    Represents the category that the :class:`AuditLogAction` belongs to.

    This can be retrieved via :attr:`AuditLogEntry.category`.

    .. attribute:: create

        The action is the creation of something.

    .. attribute:: delete

        The action is the deletion of something.

    .. attribute:: update

        The action is the update of something.

.. class:: TeamMembershipState

    Represents the membership state of a team member retrieved through :func:`Client.application_info`.

    .. versionadded:: 1.3

    .. attribute:: invited

        Represents an invited member.

    .. attribute:: accepted

        Represents a member currently in the team.

.. class:: WebhookType

    Represents the type of webhook that can be received.

    .. versionadded:: 1.3

    .. attribute:: incoming

        Represents a webhook that can post messages to channels with a token.

    .. attribute:: channel_follower

        Represents a webhook that is internally managed by Discord, used for following channels.

    .. attribute:: application

        Represents a webhook that is used for interactions or applications.

        .. versionadded:: 2.0

.. class:: ExpireBehaviour

    Represents the behaviour the :class:`Integration` should perform
    when a user's subscription has finished.

    There is an alias for this called ``ExpireBehavior``.

    .. versionadded:: 1.4

    .. attribute:: remove_role

        This will remove the :attr:`StreamIntegration.role` from the user
        when their subscription is finished.

    .. attribute:: kick

        This will kick the user when their subscription is finished.

.. class:: DefaultAvatar

    Represents the default avatar of a Discord :class:`User`

    .. attribute:: blurple

        Represents the default avatar with the color blurple.
        See also :attr:`Colour.blurple`
    .. attribute:: grey

        Represents the default avatar with the color grey.
        See also :attr:`Colour.greyple`
    .. attribute:: gray

        An alias for :attr:`grey`.
    .. attribute:: green

        Represents the default avatar with the color green.
        See also :attr:`Colour.green`
    .. attribute:: orange

        Represents the default avatar with the color orange.
        See also :attr:`Colour.orange`
    .. attribute:: red

        Represents the default avatar with the color red.
        See also :attr:`Colour.red`

.. class:: StickerType

    Represents the type of sticker.

    .. versionadded:: 2.0

    .. attribute:: standard

        Represents a standard sticker that all Nitro users can use.

    .. attribute:: guild

        Represents a custom sticker created in a guild.

.. class:: StickerFormatType

    Represents the type of sticker images.

    .. versionadded:: 1.6

    .. attribute:: png

        Represents a sticker with a png image.

    .. attribute:: apng

        Represents a sticker with an apng image.

    .. attribute:: lottie

        Represents a sticker with a lottie image.

    .. attribute:: gif

        Represents a sticker with a gif image.

        .. versionadded:: 2.4

.. class:: InviteTarget

    Represents the invite type for voice channel invites.

    .. versionadded:: 2.0

    .. attribute:: unknown

        The invite doesn't target anyone or anything.

    .. attribute:: stream

        A stream invite that targets a user.

    .. attribute:: embedded_application

        A invite that targets an embedded application.

        Note that your bot won't be verified if you provide users access to this

.. class:: InviteTargetUsersJobStatusCode

    Represents the status code for an invite target users processing job.

    .. versionadded:: 2.8

    .. attribute:: unspecified

        The job status is unspecified.

    .. attribute:: processing

        The job is currently processing.

    .. attribute:: completed

        The job has completed successfully.

    .. attribute:: failed

        The job has failed.

.. class:: VideoQualityMode

    Represents the camera video quality mode for voice channel participants.

    .. versionadded:: 2.0

    .. attribute:: auto

        Represents auto camera video quality.

    .. attribute:: full

        Represents full camera video quality.

.. class:: StagePrivacyLevel

    Represents a stage instance's privacy level.
    Stage event privacy levels can only have 1 possible value at the moment so
    this shouldn't really be used.

    .. versionadded:: 2.0

    .. attribute:: closed

        The stage instance can only be joined by members of the guild.

    .. attribute:: guild_only

        Alias for :attr:`.closed`

.. class:: NSFWLevel

    Represents the NSFW level of a guild.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two NSFW levels are equal.
        .. describe:: x != y

            Checks if two NSFW levels are not equal.
        .. describe:: x > y

            Checks if a NSFW level is higher than another.
        .. describe:: x < y

            Checks if a NSFW level is lower than another.
        .. describe:: x >= y

            Checks if a NSFW level is higher or equal to another.
        .. describe:: x <= y

            Checks if a NSFW level is lower or equal to another.

    .. attribute:: default

        The guild has not been categorised yet.

    .. attribute:: explicit

        The guild contains NSFW content.

    .. attribute:: safe

        The guild does not contain any NSFW content.

    .. attribute:: age_restricted

        The guild may contain NSFW content.

.. class:: EmbeddedActivity

    Represents an embedded activity application.

    Some might be boost-only or gated.

    .. warning::

        Discord said that they won't verify bots who gives access to embedded activities.

        Read more here: https://discord.com/channels/613425648685547541/697236247739105340/901153332075315321.

    .. versionadded:: 2.0

    .. attribute:: ask_away

        Represents the embedded application Ask Away.

        .. versionadded:: 2.4

    .. attribute:: awkword

        Represents the embedded application Awkword.

        .. warning::

            This activity has been removed.

    .. attribute:: awkword_dev

        Development version of :attr:`.awkword`.

        .. warning::

            This activity has been removed.

    .. attribute:: bash_out

        Represents the embedded application Bash Out.

        .. versionadded:: 2.4

    .. attribute:: betrayal

        Represents the embedded application Betrayal.io.

    .. attribute:: blazing_8s

        Represents the embedded application Blazing 8s.

        .. versionadded:: 2.4

    .. attribute:: blazing_8s_dev

        Development version of :attr:`.blazing_8s`.

        .. versionadded:: 2.4

    .. attribute:: blazing_8s_qa

        QA version of :attr:`.blazing_8s`.

        .. versionadded:: 2.4

    .. attribute:: blazing_8s_staging

        Staging version of :attr:`.blazing_8s`.

        .. versionadded:: 2.4

    .. attribute:: bobble_league

        Represents the embedded application Bobble League.

        .. versionadded:: 2.4

    .. attribute:: checkers_in_the_park

        Represents the embedded application Checkers in the Park.

    .. attribute:: checkers_in_the_park_dev

        Development version of :attr:`.checkers_in_the_park`.

    .. attribute:: checkers_in_the_park_qa

        QA version of :attr:`.checkers_in_the_park`.

    .. attribute:: checkers_in_the_park_staging

        Staging version of :attr:`.checkers_in_the_park`.

    .. attribute:: chess_in_the_park

        Represents the embedded application Chess in the Park.

    .. attribute:: chess_in_the_park_dev

        Development version of :attr:`.chess_in_the_park`.

    .. attribute:: chess_in_the_park_qa

        QA version of :attr:`.chess_in_the_park`.

    .. attribute:: chess_in_the_park_staging

        Staging version of :attr:`.chess_in_the_park`.

    .. attribute:: decoders_dev

        Represents the embedded application Decoders Development.

        .. warning::

            This activity has been removed.

    .. attribute:: doodle_crew

        Represents the embedded application Doodle Crew.

        .. warning::

            This activity has been removed.

    .. attribute:: doodle_crew_dev

        Development version of :attr:`.doodle_crew`.

        .. warning::

            This activity has been removed.

    .. attribute:: fishington

        Represents the embedded application Fishington.io.

    .. attribute:: gartic_phone

        Represents the embedded application Gartic Phone.

        .. versionadded:: 2.5

    .. attribute:: jamspace

        Represents the embedded application Jamspace.

        .. versionadded:: 2.5

    .. attribute:: know_what_i_meme

        Represents the embedded application Know What I Meme.

        .. versionadded:: 2.4

    .. attribute:: land

        Represents the embedded application Land.io.

        .. versionadded:: 2.4

    .. attribute:: letter_league

        Represents the embedded application Letter League.

    .. attribute:: letter_league_dev

        Development version of :attr:`.letter_league`.

        .. versionadded:: 2.4

    .. attribute:: poker_night

        Represents the embedded application Poker Night.

    .. attribute:: poker_night_dev

        Development version of :attr:`.poker_night`.

        .. versionadded:: 2.4

    .. attribute:: poker_night_qa

        QA version of :attr:`.poker_night`.

    .. attribute:: poker_night_staging

        Staging version of :attr:`.poker_night`.

    .. attribute:: putt_party

        Represents the embedded application Putt Party.

        .. versionadded:: 2.4

    .. attribute:: putt_party_dev

        Development version of :attr:`.putt_party`.

        .. versionadded:: 2.4

    .. attribute:: putt_party_qa

        QA version of :attr:`.putt_party`.

        .. versionadded:: 2.4

    .. attribute:: putt_party_staging

        Staging version of :attr:`.putt_party`.

        .. versionadded:: 2.4

    .. attribute:: putts

        Represents the embedded application Putts.

        .. warning::

            This activity has been removed.

    .. attribute:: sketch_heads

        Represents the embedded application Sketch Heads.

        .. versionadded:: 2.4

    .. attribute:: sketch_heads_dev

        Development version of :attr:`.sketch_heads`.

        .. versionadded:: 2.4

    .. attribute:: sketchy_artist

        Represents the embedded application Sketchy Artist.

        .. warning::

            This activity has been removed.

    .. attribute:: sketchy_artist_dev

        Development version of :attr:`.sketchy_artist`.

        .. warning::

            This activity has been removed.

    .. attribute:: spell_cast

        Represents the embedded application Spell Cast.

    .. attribute:: spell_cast_staging

        Staging version of :attr:`.spell_cast`.

        .. versionadded:: 2.4

    .. attribute:: watch_together

        Same as :attr:`~EmbeddedActivity.youtube_together` with remote feature which allows guild admins to limit the playlist access.

    .. attribute:: watch_together_dev

        Development version of :attr:`.watch_together`.

    .. attribute:: word_snacks

        Represents the embedded application word snacks.

    .. attribute:: word_snacks_dev

        Development version of :attr:`.word_snacks`.

    .. attribute:: youtube_together

        Represents the embedded application Youtube Together.

.. class:: ScheduledEventStatus

    Represents the status of a scheduled event.

    .. versionadded:: 2.0

    .. attribute:: scheduled

        The scheduled event hasn't started or been canceled yet.

    .. attribute:: active

        The scheduled event is in progress.

    .. attribute:: completed

        The scheduled event is over.

    .. attribute:: canceled

        The scheduled event has been canceled before it can start.

    .. attribute:: cancelled

        Alias to :attr:`canceled`.

.. class:: ScheduledEventLocationType

    Represents a scheduled event location type (otherwise known as the entity type on the API).

    .. versionadded:: 2.0

    .. attribute:: stage_instance

        Represents a scheduled event that is happening in a :class:`StageChannel`.

    .. attribute:: voice

        Represents a scheduled event that is happening in a :class:`VoiceChannel`.

    .. attribute:: external

        Represents a generic location as a :class:`str`.

.. class:: ScheduledEventPrivacyLevel

    Represents the privacy level of a scheduled event.
    Scheduled event privacy levels can only have 1 possible value at the moment so
    this shouldn't really be used.

    .. attribute:: guild_only

        Represents a scheduled event that is only available to members inside the guild.

.. class:: ApplicationRoleConnectionMetadataType

    Represents an application role connection metadata type.

    Each metadata type offers a comparison operation that allows guilds to
    configure role requirements based on metadata values stored by the bot.
    Bots specify a ``metadata value`` for each user and guilds specify the
    required ``guild's configured value`` within the guild role settings.

    .. versionadded:: 2.4

    .. attribute:: integer_less_than_or_equal

        The metadata value (``integer``) is less than or equal to the guild's configured value (``integer``).

    .. attribute:: integer_greater_than_or_equal

        The metadata value (``integer``) is greater than or equal to the guild's configured value (``integer``).

    .. attribute:: integer_equal

        The metadata value (``integer``) is equal to the guild's configured value (``integer``).

    .. attribute:: integer_not_equal

        The metadata value (``integer``) is not equal to the guild's configured value (``integer``).

    .. attribute:: datetime_less_than_or_equal

        The metadata value (``datetime``) is less than or equal to the guild's configured value
        (``integer``; the number of days before the current date).

    .. attribute:: datetime_greater_than_or_equal

        The metadata value (``datetime``) is greater than or equal to the guild's configured value
        (``integer``; the number of days before the current date).

    .. attribute:: boolean_equal

        The metadata value (``integer``) is equal to the guild's configured value (``integer``; 1).

    .. attribute:: boolean_not_equal

        The metadata value (``integer``) is not equal to the guild's configured value (``integer``; 1).

.. class:: AutoModTriggerType

    Represents an AutoMod trigger type.

    .. versionadded:: 2.0

    .. attribute:: keyword

        Represents a keyword rule trigger, which are customizable by a guild.

        Possible attributes for :class:`AutoModTriggerMetadata`:

        - :attr:`~AutoModTriggerMetadata.keyword_filter`
        - :attr:`~AutoModTriggerMetadata.regex_patterns`
        - :attr:`~AutoModTriggerMetadata.allow_list`

    .. attribute:: keyword_preset

        Represents a preset keyword rule trigger.

        Possible attributes for :class:`AutoModTriggerMetadata`:

        - :attr:`~AutoModTriggerMetadata.presets`
        - :attr:`~AutoModTriggerMetadata.allow_list`

    .. attribute:: spam

        Represents the spam rule trigger.

        There are no possible attributes for :class:`AutoModTriggerMetadata`.

    .. attribute:: mention_spam

        Represents a mention spam keyword rule trigger.

        Possible attributes for :class:`AutoModTriggerMetadata`:

        - :attr:`~AutoModTriggerMetadata.mention_total_limit`

        .. versionadded:: 2.4

    .. attribute:: harmful_link

        Represents a harmful link rule trigger.

        .. deprecated:: 2.4
            Removed by Discord and merged into :attr:`spam`.

.. class:: AutoModEventType

    Represents an AutoMod event type.

    .. versionadded:: 2.0

    .. attribute:: message_send

        Represents a message send AutoMod event.

.. class:: AutoModActionType

    Represents the type of action AutoMod is performing.

    .. versionadded:: 2.0

    .. attribute:: block_message

        Represents a block message action.

    .. attribute:: send_alert_message

        Represents a send alert message action.

    .. attribute:: timeout

        Represents a timeout action.

.. class:: AutoModKeywordPresetType

    Represents an AutoMod keyword preset type.

    .. versionadded:: 2.0

    .. attribute:: profanity

        Represents the profanity keyword preset rule.

    .. attribute:: sexual_content

        Represents the sexual content keyword preset rule.

    .. attribute:: slurs

        Represents the slurs keyword preset rule.

.. class:: PromptType

    Represents how each prompt's options are displayed.

    .. versionadded:: 2.5

    .. attribute:: multiple_choice

        The options will appear in a grid form, showing the name and description.

    .. attribute:: dropdown

        The options will appear in a dropdown (similar to select menus), but without the description displayed. This is **enforced** if there are more than 12 options in the prompt.

.. class:: OnboardingMode

    Represents the current mode of the guild's onboarding flow.

    .. versionadded:: 2.5

    .. attribute:: default

        Only default channels are counted towards the Onboarding requirements.

    .. attribute:: advanced

        Both default channels and questions (``OnboardingPrompt``\s) will count towards the Onboarding requirements.

.. class:: ReactionType

    Represents a Reaction's type.

    .. versionadded:: 2.5

    .. attribute:: normal

        Represents a normal reaction.

    .. attribute:: burst

        Represents a super reaction.

.. class:: SKUType

    Represents an SKU's type.

    .. versionadded:: 2.5

    .. attribute:: durable

       A one-time purchase that is permanent and is not subject to either renewal
       or consumption, such as lifetime access to an app's premium features.

    .. attribute:: consumable

       A one-time, non-renewable purchase that provides access, such as a temporary
       power-up or boost in a game.

    .. attribute:: subscription

        Represents a recurring subscription.

    .. attribute:: subscription_group

        A system-generated group for each subscription SKU created. These types of SKUs are currently unused.


.. class:: EntitlementType

    Represents an entitlement's type.

    .. versionadded:: 2.5

    .. attribute:: purchase

        Entitlement was purchased by the user.

    .. attribute:: premium_subscription

        Entitlement is for a Discord Nitro subscription.

    .. attribute:: developer_gift

        Entitlement was gifted by the developer.

    .. attribute:: test_mode_purchase

        Entitlement was purchased by a developer in the application's test mode.

    .. attribute:: free_purchase

        Entitlement was granted when the SKU was free.

    .. attribute:: user_gift

        Entitlement was gifted by another user.

    .. attribute:: premium_purchase

        Entitlement was claimed by a user for free as a Nitro subscriber.

    .. attribute:: application_subscription

        Entitlement was purchased as an app subscription.


.. class:: EntitlementOwnerType

    Represents an entitlement's ownership type.

    .. versionadded:: 2.5

    .. attribute:: guild

        Entitlement is owned by a guild.

    .. attribute:: user

        Entitlement is owned by a user.


.. class:: PollLayoutType

    Represents a poll's layout type.

    .. versionadded:: 2.6

    .. attribute:: default

        Represents the default layout.


.. class:: IntegrationType

    The integration type for an application.

    .. versionadded:: 2.6

    .. attribute:: guild_install

        The integration is added to a guild.

    .. attribute:: user_install

        The integration is added to a user account.


.. class:: InteractionContextType

    The context where an interaction occurs.

    .. versionadded:: 2.6

    .. attribute:: guild

        The interaction is in a guild.

    .. attribute:: bot_dm

        The interaction is in the bot's own DM channel with the user.

    .. attribute:: private_channel

        The interaction is in a private DM or group DM channel.

.. class:: VoiceChannelEffectAnimationType

    Represents the type of animation for a voice channel effect.

    .. versionadded:: 2.7

    .. attribute:: premium

        The animation is a premium effect.

    .. attribute:: basic

        The animation is a basic effect.


.. class:: SubscriptionStatus

    Represents a subscription's status.

    .. versionadded:: 2.7

    .. attribute:: active

        The subscription is active and is scheduled to renew.

    .. attribute:: ending

        The subscription is active but will not renew.

    .. attribute:: inactive

        The subscription is inactive and the subscription owner is not being charged.



.. class:: ThreadArchiveDuration

    Represents the time before a thread is archived.

    .. versionadded:: 2.7

    .. attribute:: one_hour

        Indicates that the thread will be archived after 1 hour of inactivity.

    .. attribute:: one_day

        Indicates that the thread will be archived after 1 day of inactivity.

    .. attribute:: three_days

        Indicates that the thread will be archived after 3 days of inactivity.

    .. attribute:: one_week

        Indicates that the thread will be archived after 1 week of inactivity.


.. class:: SeparatorSpacingSize

    Represents the padding size around a separator component.

    .. versionadded:: 2.7

    .. attribute:: small

        The separator uses small padding.

    .. attribute:: large

        The separator uses large padding.

.. class:: SortOrder

    Used to represent the default sort order for posts in :class:`ForumChannel` and :class:`MediaChannel`.

    .. attribute:: latest_activity

        Sort by latest activity.

    .. attribute:: creation_date

        Sort by post creation date.

.. class:: SelectDefaultValueType

    Represents the default value type of a select menu.

    .. attribute:: channel

        The default value is a channel.

    .. attribute:: role

        The default value is a role.

    .. attribute:: user

        The default value is a user.
