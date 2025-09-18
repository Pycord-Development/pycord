.. currentmodule:: discord

.. _discord_api_models:

Discord Models
==============

Models are classes that are received from Discord and are not meant to be created by
the user of the library.

.. danger::

    The classes listed below are **not intended to be created by users** and are also
    **read-only**.

    For example, this means that you should not make your own :class:`User` instances
    nor should you modify the :class:`User` instance yourself.

    If you want to get one of these model classes instances they'd have to be through
    the cache, and a common way of doing so is through the :func:`utils.find` function
    or attributes of model classes that you receive from the events specified in the
    :ref:`discord-api-events`.

.. note::

    Nearly all classes here have :ref:`py:slots` defined which means that it is
    impossible to have dynamic attributes to the data classes.


.. attributetable:: Asset

.. autoclass:: Asset()
    :members:
    :inherited-members:

.. attributetable:: Spotify

.. autoclass:: Spotify()
    :members:

.. attributetable:: VoiceState

.. autoclass:: VoiceState()
    :members:

.. attributetable:: PartialMessageable

.. autoclass:: PartialMessageable()
    :members:
    :inherited-members:

Users
-----

.. attributetable:: ClientUser

.. autoclass:: ClientUser()
    :members:
    :inherited-members:

.. attributetable:: User

.. autoclass:: User()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Messages
--------

.. attributetable:: Attachment

.. autoclass:: Attachment()
    :members:

.. attributetable:: Message

.. autoclass:: Message()
    :members:

.. attributetable:: DeletedReferencedMessage

.. autoclass:: DeletedReferencedMessage()
    :members:

.. attributetable:: Reaction

.. autoclass:: Reaction()
    :members:
    :exclude-members: users

    .. automethod:: users
        :async-for:

.. autoclass:: ReactionCountDetails()
    :members:

Monetization
------------

.. attributetable:: SKU

.. autoclass:: SKU()
    :members:

.. attributetable:: Entitlement

.. autoclass:: Entitlement()
    :members:

.. attributetable:: Subscription

.. autoclass:: Subscription()
    :members:

Guild
-----

.. attributetable:: Guild

.. autoclass:: Guild()
    :members:
    :exclude-members: fetch_members, audit_logs

    .. automethod:: fetch_members
        :async-for:

    .. automethod:: audit_logs
        :async-for:

.. class:: BanEntry

    A namedtuple which represents a ban returned from :meth:`~Guild.bans`.

    .. attribute:: reason

        The reason this user was banned.

        :type: Optional[:class:`str`]
    .. attribute:: user

        The :class:`User` that was banned.

        :type: :class:`User`

.. attributetable:: Member

.. autoclass:: Member()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

.. attributetable:: Template

.. autoclass:: Template()
    :members:

AutoMod
~~~~~~~

.. attributetable:: AutoModRule

.. autoclass:: AutoModRule()
    :members:

.. attributetable:: AutoModAction

.. autoclass:: AutoModAction()
    :members:

.. attributetable:: AutoModActionMetadata

.. autoclass:: AutoModActionMetadata()
    :members:

.. attributetable:: AutoModTriggerMetadata

.. autoclass:: AutoModTriggerMetadata()
    :members:

Invites
~~~~~~~

.. attributetable:: PartialInviteGuild

.. autoclass:: PartialInviteGuild()
    :members:

.. attributetable:: PartialInviteChannel

.. autoclass:: PartialInviteChannel()
    :members:

.. attributetable:: Invite

.. autoclass:: Invite()
    :members:

Role
~~~~

.. attributetable:: Role

.. autoclass:: Role()
    :members:

.. attributetable:: RoleTags

.. autoclass:: RoleTags()
    :members:

.. attributetable:: RoleColours

.. autoclass:: RoleColours
    :members:

Scheduled Event
~~~~~~~~~~~~~~~

.. attributetable:: ScheduledEvent

.. autoclass:: ScheduledEvent()
    :members:

.. autoclass:: ScheduledEventLocation()
    :members:

Welcome Screen
~~~~~~~~~~~~~~

.. attributetable:: WelcomeScreen

.. autoclass:: WelcomeScreen()
    :members:

.. attributetable:: WelcomeScreenChannel

.. autoclass:: WelcomeScreenChannel()
    :members:

Onboarding
~~~~~~~~~~~~~~

.. attributetable:: Onboarding

.. autoclass:: Onboarding()
    :members:

.. attributetable:: OnboardingPrompt

.. autoclass:: OnboardingPrompt()
    :members:

.. attributetable:: PromptOption

.. autoclass:: PromptOption()
    :members:

Integration
~~~~~~~~~~~

.. autoclass:: Integration()
    :members:

.. autoclass:: IntegrationAccount()
    :members:

.. autoclass:: BotIntegration()
    :members:

.. autoclass:: IntegrationApplication()
    :members:

.. autoclass:: StreamIntegration()
    :members:

Widget
~~~~~~

.. attributetable:: Widget

.. autoclass:: Widget()
    :members:

.. attributetable:: WidgetChannel

.. autoclass:: WidgetChannel()
    :members:

.. attributetable:: WidgetMember

.. autoclass:: WidgetMember()
    :members:
    :inherited-members:

Threads
~~~~~~~

.. attributetable:: Thread

.. autoclass:: Thread()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

.. attributetable:: ThreadMember

.. autoclass:: ThreadMember()
    :members:

Stages
~~~~~~

.. attributetable:: StageChannel

.. autoclass:: StageChannel()
    :members:
    :inherited-members:

.. attributetable:: StageInstance

.. autoclass:: StageInstance()
    :members:

Interactions
------------

.. attributetable:: Interaction

.. autoclass:: Interaction()
    :members:

.. attributetable:: InteractionResponse

.. autoclass:: InteractionResponse()
    :members:

.. attributetable:: InteractionMessage

.. autoclass:: InteractionMessage()
    :members:

.. attributetable:: MessageInteraction

.. autoclass:: MessageInteraction()
    :members:

.. attributetable:: InteractionMetadata

.. autoclass:: InteractionMetadata()
    :members:

.. attributetable:: AuthorizingIntegrationOwners

.. autoclass:: AuthorizingIntegrationOwners()
    :members:

.. attributetable:: InteractionCallback

.. autoclass:: InteractionCallback()
    :members:

Message Components
------------------

.. attributetable:: Component

.. autoclass:: Component()
    :members:

.. attributetable:: ActionRow

.. autoclass:: ActionRow()
    :members:

.. attributetable:: Button

.. autoclass:: Button()
    :members:
    :inherited-members:

.. attributetable:: SelectMenu

.. autoclass:: SelectMenu()
    :members:
    :inherited-members:

.. attributetable:: Section

.. autoclass:: Section()
    :members:
    :inherited-members:

.. attributetable:: TextDisplay

.. autoclass:: TextDisplay()
    :members:
    :inherited-members:

.. attributetable:: Thumbnail

.. autoclass:: Thumbnail()
    :members:
    :inherited-members:

.. attributetable:: MediaGallery

.. autoclass:: MediaGallery()
    :members:
    :inherited-members:

.. attributetable:: FileComponent

.. autoclass:: FileComponent()
    :members:
    :inherited-members:

.. attributetable:: Separator

.. autoclass:: Separator()
    :members:
    :inherited-members:

.. attributetable:: Container

.. autoclass:: Container()
    :members:
    :inherited-members:

.. attributetable:: FileUpload

.. autoclass:: FileUpload()
    :members:
    :inherited-members:

Emoji
-----

.. attributetable:: GuildEmoji

.. autoclass:: GuildEmoji()
    :members:
    :inherited-members:

.. attributetable:: AppEmoji

.. autoclass:: AppEmoji()
    :members:
    :inherited-members:

.. attributetable:: PartialEmoji

.. autoclass:: PartialEmoji()
    :members:
    :inherited-members:

Channels
--------

.. attributetable:: TextChannel

.. autoclass:: TextChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

.. attributetable:: ForumChannel

.. autoclass:: ForumChannel()
    :members:
    :inherited-members:

.. attributetable:: MediaChannel

.. autoclass:: MediaChannel()
    :members:
    :inherited-members:

.. attributetable:: VoiceChannel

.. autoclass:: VoiceChannel()
    :members:
    :inherited-members:

.. attributetable:: CategoryChannel

.. autoclass:: CategoryChannel()
    :members:
    :inherited-members:

.. attributetable:: DMChannel

.. autoclass:: DMChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

.. attributetable:: GroupChannel

.. autoclass:: GroupChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Stickers
--------

.. attributetable:: Sticker

.. autoclass:: Sticker()
    :members:

.. attributetable:: StickerPack

.. autoclass:: StickerPack()
    :members:

.. attributetable:: StickerItem

.. autoclass:: StickerItem()
    :members:

.. attributetable:: StandardSticker

.. autoclass:: StandardSticker()
    :members:

.. attributetable:: GuildSticker

.. autoclass:: GuildSticker()
    :members:

Soundboard
----------

.. attributetable:: PartialSoundboardSound

.. autoclass:: PartialSoundboardSound()
    :members:

.. attributetable:: SoundboardSound

.. autoclass:: SoundboardSound()
    :members:
    :inherited-members:

Events
------

.. attributetable:: AutoModActionExecutionEvent

.. autoclass:: AutoModActionExecutionEvent()
    :members:

.. attributetable:: RawTypingEvent

.. autoclass:: RawTypingEvent()
    :members:

.. attributetable:: RawMessageDeleteEvent

.. autoclass:: RawMessageDeleteEvent()
    :members:

.. attributetable:: RawBulkMessageDeleteEvent

.. autoclass:: RawBulkMessageDeleteEvent()
    :members:

.. attributetable:: RawMessageUpdateEvent

.. autoclass:: RawMessageUpdateEvent()
    :members:

.. attributetable:: RawReactionActionEvent

.. autoclass:: RawReactionActionEvent()
    :members:

.. attributetable:: RawReactionClearEvent

.. autoclass:: RawReactionClearEvent()
    :members:

.. attributetable:: RawReactionClearEmojiEvent

.. autoclass:: RawReactionClearEmojiEvent()
    :members:

.. attributetable:: RawIntegrationDeleteEvent

.. autoclass:: RawIntegrationDeleteEvent()
    :members:

.. attributetable:: RawThreadDeleteEvent

.. autoclass:: RawThreadDeleteEvent()
    :members:

.. attributetable:: RawScheduledEventSubscription

.. autoclass:: RawScheduledEventSubscription()
    :members:

.. attributetable:: RawMemberRemoveEvent

.. autoclass:: RawMemberRemoveEvent()
    :members:

.. attributetable:: RawThreadUpdateEvent

.. autoclass:: RawThreadUpdateEvent()
    :members:

.. attributetable:: RawThreadMembersUpdateEvent

.. autoclass:: RawThreadMembersUpdateEvent()
    :members:

.. attributetable:: RawAuditLogEntryEvent

.. autoclass:: RawAuditLogEntryEvent()
    :members:

.. attributetable:: RawVoiceChannelStatusUpdateEvent

.. autoclass:: RawVoiceChannelStatusUpdateEvent()
    :members:

.. attributetable:: VoiceChannelEffectSendEvent

.. autoclass:: VoiceChannelEffectSendEvent()
    :members:



Webhooks
--------

.. attributetable:: PartialWebhookGuild

.. autoclass:: PartialWebhookGuild()
    :members:

.. attributetable:: PartialWebhookChannel

.. autoclass:: PartialWebhookChannel()
    :members:



Collectibles
------------

.. attributetable:: Nameplate

.. autoclass:: Nameplate()
    :undoc-members:
