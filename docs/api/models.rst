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


ClientUser
----------

.. attributetable:: ClientUser

.. autoclass:: ClientUser()
    :members:
    :inherited-members:

User
----

.. attributetable:: User

.. autoclass:: User()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Attachment
----------

.. attributetable:: Attachment

.. autoclass:: Attachment()
    :members:

Asset
-----

.. attributetable:: Asset

.. autoclass:: Asset()
    :members:
    :inherited-members:

Message
-------

.. attributetable:: Message

.. autoclass:: Message()
    :members:

Component
---------

.. attributetable:: Component

.. autoclass:: Component()
    :members:

ActionRow
---------

.. attributetable:: ActionRow

.. autoclass:: ActionRow()
    :members:

Button
------

.. attributetable:: Button

.. autoclass:: Button()
    :members:
    :inherited-members:

SelectMenu
----------

.. attributetable:: SelectMenu

.. autoclass:: SelectMenu()
    :members:
    :inherited-members:


DeletedReferencedMessage
------------------------

.. attributetable:: DeletedReferencedMessage

.. autoclass:: DeletedReferencedMessage()
    :members:


Reaction
--------

.. attributetable:: Reaction

.. autoclass:: Reaction()
    :members:
    :exclude-members: users

    .. automethod:: users
        :async-for:

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

ScheduledEvent
--------------

.. attributetable:: ScheduledEvent

.. autoclass:: ScheduledEvent()
    :members:

.. autoclass:: ScheduledEventLocation()
    :members:

Integration
-----------

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

Interaction
-----------

.. attributetable:: Interaction

.. autoclass:: Interaction()
    :members:

InteractionResponse
-------------------

.. attributetable:: InteractionResponse

.. autoclass:: InteractionResponse()
    :members:

InteractionMessage
------------------

.. attributetable:: InteractionMessage

.. autoclass:: InteractionMessage()
    :members:

MessageInteraction
------------------

.. attributetable:: MessageInteraction

.. autoclass:: MessageInteraction()
    :members:

Member
------

.. attributetable:: Member

.. autoclass:: Member()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

Spotify
-------

.. attributetable:: Spotify

.. autoclass:: Spotify()
    :members:

VoiceState
----------

.. attributetable:: VoiceState

.. autoclass:: VoiceState()
    :members:

Emoji
-----

.. attributetable:: Emoji

.. autoclass:: Emoji()
    :members:
    :inherited-members:

PartialEmoji
------------

.. attributetable:: PartialEmoji

.. autoclass:: PartialEmoji()
    :members:
    :inherited-members:

Role
----

.. attributetable:: Role

.. autoclass:: Role()
    :members:

RoleTags
--------

.. attributetable:: RoleTags

.. autoclass:: RoleTags()
    :members:

PartialMessageable
------------------

.. attributetable:: PartialMessageable

.. autoclass:: PartialMessageable()
    :members:
    :inherited-members:

TextChannel
-----------

.. attributetable:: TextChannel

.. autoclass:: TextChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

ForumChannel
------------

.. attributetable:: ForumChannel

.. autoclass:: ForumChannel()
    :members:
    :inherited-members:

Thread
------

.. attributetable:: Thread

.. autoclass:: Thread()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

ThreadMember
------------

.. attributetable:: ThreadMember

.. autoclass:: ThreadMember()
    :members:

VoiceChannel
------------

.. attributetable:: VoiceChannel

.. autoclass:: VoiceChannel()
    :members:
    :inherited-members:

StageChannel
------------

.. attributetable:: StageChannel

.. autoclass:: StageChannel()
    :members:
    :inherited-members:


StageInstance
-------------

.. attributetable:: StageInstance

.. autoclass:: StageInstance()
    :members:

CategoryChannel
---------------

.. attributetable:: CategoryChannel

.. autoclass:: CategoryChannel()
    :members:
    :inherited-members:

DMChannel
---------

.. attributetable:: DMChannel

.. autoclass:: DMChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

GroupChannel
------------

.. attributetable:: GroupChannel

.. autoclass:: GroupChannel()
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: history
        :async-for:

    .. automethod:: typing
        :async-with:

PartialInviteGuild
------------------

.. attributetable:: PartialInviteGuild

.. autoclass:: PartialInviteGuild()
    :members:

PartialInviteChannel
--------------------

.. attributetable:: PartialInviteChannel

.. autoclass:: PartialInviteChannel()
    :members:

Invite
------

.. attributetable:: Invite

.. autoclass:: Invite()
    :members:

Template
--------

.. attributetable:: Template

.. autoclass:: Template()
    :members:

WelcomeScreen
-------------

.. attributetable:: WelcomeScreen

.. autoclass:: WelcomeScreen()
    :members:

WelcomeScreenChannel
--------------------

.. attributetable:: WelcomeScreenChannel

.. autoclass:: WelcomeScreenChannel()
    :members:

WidgetChannel
-------------

.. attributetable:: WidgetChannel

.. autoclass:: WidgetChannel()
    :members:

WidgetMember
------------

.. attributetable:: WidgetMember

.. autoclass:: WidgetMember()
    :members:
    :inherited-members:

Widget
------

.. attributetable:: Widget

.. autoclass:: Widget()
    :members:

StickerPack
-----------

.. attributetable:: StickerPack

.. autoclass:: StickerPack()
    :members:

StickerItem
-----------

.. attributetable:: StickerItem

.. autoclass:: StickerItem()
    :members:

Sticker
-------

.. attributetable:: Sticker

.. autoclass:: Sticker()
    :members:

StandardSticker
---------------

.. attributetable:: StandardSticker

.. autoclass:: StandardSticker()
    :members:

GuildSticker
------------

.. attributetable:: GuildSticker

.. autoclass:: GuildSticker()
    :members:

AutoModRule
-----------

.. attributetable:: AutoModRule

.. autoclass:: AutoModRule()
    :members:

AutoModActionExecutionEvent
---------------------------

.. attributetable:: AutoModActionExecutionEvent

.. autoclass:: AutoModActionExecutionEvent()
    :members:

RawTypingEvent
--------------

.. attributetable:: RawTypingEvent

.. autoclass:: RawTypingEvent()
    :members:

RawMessageDeleteEvent
---------------------

.. attributetable:: RawMessageDeleteEvent

.. autoclass:: RawMessageDeleteEvent()
    :members:

RawBulkMessageDeleteEvent
-------------------------

.. attributetable:: RawBulkMessageDeleteEvent

.. autoclass:: RawBulkMessageDeleteEvent()
    :members:

RawMessageUpdateEvent
---------------------

.. attributetable:: RawMessageUpdateEvent

.. autoclass:: RawMessageUpdateEvent()
    :members:

RawReactionActionEvent
----------------------

.. attributetable:: RawReactionActionEvent

.. autoclass:: RawReactionActionEvent()
    :members:

RawReactionClearEvent
---------------------

.. attributetable:: RawReactionClearEvent

.. autoclass:: RawReactionClearEvent()
    :members:

RawReactionClearEmojiEvent
--------------------------

.. attributetable:: RawReactionClearEmojiEvent

.. autoclass:: RawReactionClearEmojiEvent()
    :members:

RawIntegrationDeleteEvent
-------------------------

.. attributetable:: RawIntegrationDeleteEvent

.. autoclass:: RawIntegrationDeleteEvent()
    :members:

RawThreadDeleteEvent
--------------------

.. attributetable:: RawThreadDeleteEvent

.. autoclass:: RawThreadDeleteEvent()
    :members:

RawScheduledEventSubscription
-----------------------------

.. attributetable:: RawScheduledEventSubscription

.. autoclass:: RawScheduledEventSubscription()
    :members:

PartialWebhookGuild
-------------------

.. attributetable:: PartialWebhookGuild

.. autoclass:: PartialWebhookGuild()
    :members:

PartialWebhookChannel
---------------------

.. attributetable:: PartialWebhookChannel

.. autoclass:: PartialWebhookChannel()
    :members:
