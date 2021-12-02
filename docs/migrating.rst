.. currentmodule:: discord

.. _migrating_2_0:

Migrating to v2.0
=================

v2.0 includes many breaking changes and added features.

This update adds new features from the discord API such as application commands (slash, user, and message), as well as
message components and much more.

Since Pycord is still relatively new, we have attempted to make the migration from discord.py and v1 to pycord and v2 as
smooth as possible.

Python Version Change
---------------------

In order to make development easier and also to allow for our dependencies to upgrade to allow usage of 3.10 or higher,
the library had to remove support for Python versions lower than 3.8, which essentially means that **support for Python
3.7 is dropped**.

Migration to Pycord
-------------------

We have tried to make the migration as smooth as possible. The only breaking changes that we have made are improvements,
not deletions in favor of a new style. We're going to provide as much backwards support as possible, though there will
be some changes to the API as is to be expected in major releases.

New Package Name
~~~~~~~~~~~~~~~~
The package name has been changed from ``discord.py`` to ``py-cord``, because our package is a fork of the original
discord.py package.

Breaking Changes
----------------
The following changes are breaking changes, and will cause your code to stop working if you use any of these features.

User Account Support Removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
User account ("userbot") is no longer supported. Thus, many features that were only applicable to them have been
removed. Please note, this means that detection of Nitro is no longer possible.

**Removed**

The following features have been removed due to being solely related to user account support

- The ``bot`` parameter of :meth:`Client.start`/:meth:`Client.run`
- The ``afk`` parameter of :meth:`Client.change_presence`
- All of the following classes and types:
    - ``Profile``
    - ``Relationship``
    - ``CallMessage``
    - ``GroupCall``
    - ``RelationshipType``
    - ``HypeSquadHouse``
    - ``PremiumType``
    - ``UserContentFilter``
    - ``FriendFlags``
    - ``Theme``
    - ``RelationshipType``
- The following methods of :class:`GroupChannel`:
    - ``add_recipients``
    - ``remove_recipients``
    - ``edit``
- The ``ack`` method of :class:`Guild`
- The ``call`` and ``ack`` methods of :class:`Message`
- The ``fetch_user_profile`` method of :class:`Client`

Use of timezone-aware datetime
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Datetime objects are now required to be timezone-aware by the library internals. This means that you will need to
convert your datetime objects to a timezone-aware datetime object (or make them timezone-aware from the beginning)
before passing them to the library. Instead of ``datetime.datetime.utcnow``, you should use
``datetime.datetime.now(datetime.timezone.utc)``. If you are constructing a datetime object yourself, you should pass
``datetime.timezone.utc`` to the ``tzinfo`` parameter.

.. code-block:: python

   embed = discord.Embed(
       title = "Pi Day 2021 in UTC",
       timestamp = datetime(2021, 3, 14, 15, 9, 2, tzinfo=timezone.utc)
   )


Methods of :class:`Client`
~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``request_offline_members``
    This has been depreciated since v1.5.
- ``logout``
    This was an alias for :meth:`Client.close`, which is now the preferred method.

Embed __bool__ method changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``__bool__`` method of :class:`Embed` has been changed (affects ``bool(Embed)``). It will now always return truthy
values. Previously it only considered text fields.

Duplicate registration of cogs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:meth:`Bot.add_cog` now raises when a cog with the same name is already registered. The ``override`` argument can be
used to bring back the 1.x behavior.

ExtensionNotFound.original removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``original`` attribute of :class:`ExtensionNotFound` has been removed. This previously returned ``None`` for
compatibility.

MemberCacheFlags.online removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Due to a Discord limitation, the ``online`` attribute of :class:`MemberCacheFlags` has been removed.

Message.type for replies changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:attr:`Message.type` has been changed for replies. It now returns :attr:`MessageType.reply` instead of
:attr:`MessageType.default`.

Private channel events removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``private_channel_create`` and ``private_channel_delete`` events will no longer be dispatched due to Discord
limitations.

Command clean_params type changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :attr:`~.ext.commands.Command.clean_params` attribute of :class:`ext.commands.Command` has been changed to return a
:class:`dict` instead of an ``OrderedDict``.

DMChannel recipient changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~
:attr:`DMChannel.recipient` is now optional, and will return ``None`` in many cases.

User and Member permissions_in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use :meth:`abc.GuildChannel.permissions_for` instead.

GuildChannel permissions_for changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The :meth:`abc.GuildChannel.permissions_for` method's first argument is now positional only.

Client guild_subscriptions removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``guild_subscriptions`` attribute of :class:`Client` has been removed, as it has been replaced by the
:ref:`intents <intents_primer>` system.

Webhook changes
~~~~~~~~~~~~~~~

:class:`Webhook` was overhauled.

- :class:`Webhook` and :class:`WebhookMessage` are now always asynchronous. For synchronous usage (requests), use :class:`SyncWebhook` and :class:`SyncWebhookMessage`.
- ``WebhookAdapter``, ``AsyncWebhookAdapter``, and ``RequestsWebhookAdapter`` have been removed as they are unnecessary.
- ``adapter`` arguments of :meth:`Webhook.partial` and :meth:`Webhook.from_url` have been removed. Sessions are now passed directly to these methods.

.. code-block:: python

   webhook = discord.SyncWebhook.from_url(
       f"https://discord.com/api/webhooks/{id}/{token}"
   )
   webhook.send("Hello from pycord 2.0")


.. code-block:: python

   async with aiohttp.ClientSession() as session:
       webhook = discord.Webhook.partial(
           id,
           token,
           session=session
       )
       await webhook.send("Hello from pycord 2.0")


HelpCommand clean_prefix removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``clean_prefix`` attribute of :class:`HelpCommand` has been removed. This was moved to
:attr:`ext.commands.Context.clean_prefix`


Sticker preview image removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``preview_image`` attribute of :class:`Sticker` has been removed, as Discord no longer provides the data needed for
this.


Asset Changes
~~~~~~~~~~~~~
Assets have been changed.

- Asset-related attributes that previously returned hash strings (e.g. :attr:`User.avatar`) now return :class:`Asset`.
  :attr:`Asset.key` returns the hash from now on.
- ``Class.x_url`` and ``Class.x_url_as`` (e.g. ``User.avatar_url`` and ``Guild.icon_url_as``) have been removed.
  :meth:`Asset.replace` or :class:`Asset`.with_x (e.g. :meth:`Asset.with_size`) methods can be used to get specific
  asset sizes or types.
- :attr:`Emoji.url` and :attr:`PartialEmoji.url` are now :class:`str`. :meth:`Emoji.save` and :meth:`Emoji.read` are
  added to save or read emojis.
- :meth:`Emoji.url_as` and :meth:`PartialEmoji.url_as` have been removed.
- The :attr:`~.AuditLogDiff.splash`, :attr:`~.AuditLogDiff.icon`, and :attr:`~.AuditLogDiff.avatar` attributes of
  :class:`AuditLogDiff` now return :class:`Asset` instead of :class:`str`.
- :attr:`User.avatar` now returns ``None`` if the avatar is not set and is instead the default avatar;
  use :attr:`User.display_avatar` for pre-2.0 behavior.


.. code-block:: python

   avatar_url = user.display_avatar.url # previously str(avatar_url)
   avatar_128x128_url = user.display_avatar.with_size(128).url # previously str(avatar_url_as(size=128))
   avatar_128x128_png_url = user.display_avatar.replace(size=128, static_format="png").url
   # previously str(avatar_url_as(size=128, static_format="png"))
   # The code above can also be written as:
   avatar_128x128_png_url = user.display_avatar.with_size(128).with_static_format("png").url

   avatar_bytes = await user.display_avatar.read() # previously avatar_url.read

   # Emoji and Sticker are special case:
   emoji_url = emoji.url # previously str(emoji.url)
   emoji_32x32_url = emoji.with_size(32).url # previously str(emoji.url_as(size=32))
   emoji_32x32_png_url = emoji.replace(size=32, static_format="png").url
   # previously str(url_as(size=128, static_format="png"))

   emoji_bytes = await emoji.read() # previously emoji.url.read
   # Same applies to Sticker and PartialEmoji.



Color blurple changed
~~~~~~~~~~~~~~~~~~~~~
The ``Colour.blurple`` method has been changed to :meth:`Colour.og_blurple`, and :meth:`Colour.blurple` now returns
the new theme color.

``self_bot`` argument
~~~~~~~~~~~~~~~~~~~~~
The ``self_bot`` argument of :class:`~.ext.commands.Bot` has been removed, since user bots are no longer supported.

VerificationLevel attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``table_flip`` (alias of :attr:`~.VerificationLevel.high`) attribute of :class:`VerificationLevel` has been removed.
The ``extreme``, ``very_high``, and ``double_table_flip`` attributes were removed and have been replaced with
:attr:`~.VerificationLevel.highest`.


Arguments of ``oauth_url`` changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``permissions``, ``guild``, ``redirect_uri``, and ``scopes`` arguments of :func:`utils.oauth_url` have been changed
to be keyword only.


StageChannel changes
~~~~~~~~~~~~~~~~~~~~
Due to the introduction of :class:`StageInstance`, which represents the current session of a :class:`StageChannel`;

- :meth:`StageChannel.edit` can no longer be used to edit :attr:`~.StageChannel.topic`. Use :meth:`StageInstance.edit`
  instead.
- :meth:`StageChannel.clone` no longer clones its topic.


Message channel attribute changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:attr:`Message.channel` can now return :class:`Thread`.


Guild methods changed
~~~~~~~~~~~~~~~~~~~~~
The :meth:`~.Guild.get_channel`, :meth:`~.Guild.get_role`, :meth:`~.Guild.get_member_named`,
:meth:`~.Guild.fetch_member`, and :meth:`~.Guild.fetch_emoji` methods' first arguments are now positional only.


Guild create_text_channel topic argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``topic`` argument of :meth:`Guild.create_text_channel` no longer accepts ``None``.


Reaction custom emoji
~~~~~~~~~~~~~~~~~~~~~
The ``custom_emoji`` attribute of :class:`Reaction` has been replaced with the :meth:`Reaction.is_custom_emoji` method
for consistency.


Reaction users arguments changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Arguments of :meth:`Reaction.users` have been changed to be keyword only.


IntegrationAccount id attribute changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:attr:`IntegrationAccount.id` is now a :class:`str` instead of an :class:`int`, due to Discord changes.


BadInviteArgument arguments changed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:


Where Is The 1.0.0 Migation Page?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The v1.0 migration guide can be found at :ref:`migrating_1_0`.