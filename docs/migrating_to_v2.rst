.. currentmodule:: discord

.. _migrating_2_0:

Migrating to v2.0
=================

v2.0 introduced new Discord features and deprecated some old ones.

Part of the redesign involves making application commands and components. These changes include a new :class:`Bot` class, :class:`ui.View`, and a new :class:`ApplicationContext` class. If you're interested in creating them, please check out our :resource:`guide <guide>`.

Python Version Change
---------------------

In order to make development easier and also to allow for our dependencies to upgrade to allow usage of 3.8 or higher,
the library had to remove support for Python versions lower than 3.7, which essentially means that **support for Python 3.7 and below
has been dropped**.

Major Model Changes
-------------------

Below are major changes that have happened in v2.0:

Dropped User Accounts Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before v2.0, user accounts were supported. This has been against the spirit of the library and discord ToS and has been removed. Thus, these features that were only applicable to them are removed:

- ``bot`` argument of :meth:`Client.start` and :meth:`Client.run`
- ``afk`` argument of :meth:`Client.change_presence`
- Classes ``Profile``, ``Relationship``, ``Call Message``, ``Group Call``
- ``RelationshipType``, ``HypeSquadHouse``, ``PremiumType``, ``UserContentFilter``, ``FriendFlags``, ``Theme``
- ``GroupChannel.add_recipients``, ``remove_recipients``, ``edit`` (NOTE: ``GroupChannel`` itself still remains)
- ``Guild.ack``
- ``Client.self_bot``
- ``Client.fetch_user_profile``
- ``Message.call`` and ``ack``
- ``ClientUser.email``, ``premium``, ``premium_type``, ``get_relationship``, ``relationships``, ``friends``, ``blocked``, ``create_group``, ``edit_settings``
- Arguments of ``ClientUser.edit``: ``password``, ``new_password``, ``email``, ``house``
- ``User.relationship``, ``mutual_friends``, ``is_friend``, ``is_blocked``, ``block``, ``unblock``, ``remove_friend``, ``send_friend_request``, ``profile``
- Events: ``on_relationship_add`` and ``on_relationship_update``

Timezone-aware Time
~~~~~~~~~~~~~~~~~~~

``utcnow`` becomes ``now(datetime.timezone.utc)``. If you are constructing :class:`datetime.datetime`` yourself, pass ``tzinfo=datetime.timezone.utc``.

.. code-block:: python

    embed = discord.Embed(
        title = "Pi Day 2021 in UTC",
        timestamp = datetime(2021, 3, 14, 15, 9, 2, tzinfo=timezone.utc)
    )


Note that newly-added :meth:`utils.utcnow()` can be used as an alias of ``datetime.datetime.now(datetime.timezone.utc)``.

.. _migrating_2_0_model_state:

Asset Changes
~~~~~~~~~~~~~

Asset-related attributes that previously returned hash strings (e.g. :attr:`User.avatar`) now returns :class:`Asset`. :attr:`Asset.key` returns the hash from now on.

- ``Class.x_url`` and ``Class.x_url_as`` are removed. :meth:`Asset.replace` or :meth:`Asset.with_x` methods can be used to get specific asset sizes or types.
- :attr:`Emoji.url` and :attr:`PartialEmoji.url` are now :class:`str`. :meth:`Emoji.save` and :meth:`Emoji.read` are added to save or read emojis.
- ``Emoji.url_as`` and ``PartialEmoji.url_as`` are removed.
- Some :class:`AuditLogDiff` attributes now return :class:`Asset` instead of :class:`str`: :attr:`AuditLogDiff.splash`, :attr:`AuditLogDiff.icon`, :attr:`AuditLogDiff.avatar`
- :attr:`User.avatar` returns ``None`` if the avatar is not set and is instead the default avatar; use :attr:`User.display_avatar` for pre-2.0 behavior.

+------------------------------------------------------------+----------------------------------------------------------------------+
| Before                                                     | After                                                                |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(user.avatar_url)``                                   | ``user.display_avatar.url``                                          |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(user.avatar_url_as(size=128))``                      | ``user.display_avatar.with_size(128).url``                           |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(user.avatar_url_as(size=128, static_format="png"))`` | ``user.display_avatar.replace(size=128, static_format="png").url``   |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(user.avatar_url_as(size=128, static_format="png"))`` | ``user.display_avatar.with_size(128).with_static_format("png").url`` |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``await user.avatar_url.read()``                           | ``await user.display_avatar.read()``                                 |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(emoji.url)``                                         | ``emoji.url``                                                        |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(emoji.url_as(size=32))``                             | ``emoji.with_size(32).url``                                          |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(url_as(size=128, static_format="png"))``             | ``emoji.replace(size=128, static_format="png").url``                 |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(sticker.image_url)``                                 | ``sticker.url``                                                      |
+------------------------------------------------------------+----------------------------------------------------------------------+
| ``str(partialemoji.url)``                                  | ``partialemoji.url``                                                 |
+------------------------------------------------------------+----------------------------------------------------------------------+

Webhook Changes
~~~~~~~~~~~~~~~

- :class:`Webhook` and :class:`WebhookMessage` are now always asynchronous. For synchronous use (``requests``), use :class:`SyncWebhook` and :class:`SyncWebhookMessage`.
- ``WebhookAdapter``, ``AsyncWebhookAdapter``, and ``RequestsWebhookAdapter`` are removed, since they are unnecessary.
- ``adapter`` arguments of :meth:`Webhook.partial` and :meth:`Webhook.from_url` are removed. Sessions are now passed directly to ``partial`` / ``from_url``.


.. code-block:: python

    webhook = discord.SyncWebhook.from_url(
        f"https://discord.com/api/webhooks/{id}/{token}"
    )
    webhook.send("Hello from Pycord 2.0")


.. code-block:: python
    
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.partial(
            id,
            token,
            session=session
        )
        await webhook.send("Hello from Pycord 2.0")


.. _migrating_2_0_intents_changes:

Intents Changes
---------------

:attr:`Intents.message_content` is now a privileged intent. Disabling it causes :attr:`Message.content`,
:attr:`Message.embeds`, :attr:`Message.components`, and :attr:`Message.attachments` to be empty (an empty string
or an empty array), directly causing :class:`ext.commands.Command`s to not run.
See `here <https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-FAQ>`_ for more information.


.. _migrating_2_0_thread_introduced:

Threads Introduced
------------------

The following methods and attributes can return :class:`Thread` objects:

- :attr:`Message.channel`
- :meth:`Client.fetch_channel`
- :meth:`Guild.fetch_channel`
- :attr:`ext.commands.ChannelNotReadable.argument`
- :class:`ext.commands.NSFWChannelRequired`'s ``channel`` argument
- :meth:`Client.get_channel`

.. _migrating_2_0_permission_changes:

Permission Changes
------------------

``permissions_in`` has been removed in favor of checking the permissions of the channel for said user.

+---------------------------+--------------------------------------+
| Before                    | After                                |
+---------------------------+--------------------------------------+
| ``User.permissions_in``   | ``abc.GuildChannel.permissions_for`` |
+---------------------------+--------------------------------------+
| ``Member.permissions_in`` | ``abc.GuildChannel.permissions_for`` |
+---------------------------+--------------------------------------+

.. _migrating_2_0_edit_method_behavior_change:

Edit Method Behavior Change
---------------------------

``edit`` methods of most classes no longer update the cache in-place, and instead returns the modified object.

.. _migrating_2_0_positional_keyword_arguments:

Positional-Keyword Argument Split
---------------------------------

The following are now positional only:

- :meth:`abc.GuildChannel.permissions_for`
- :meth:`Guild.get_channel`
- :meth:`Guild.get_role`
- :meth:`Guild.get_member_named`
- :meth:`Guild.fetch_member`
- :meth:`Guild.fetch_emoji`
- :meth:`abc.Messageable.fetch_message`
- :meth:`PartialMessageable.get_partial_message`

The following are now keyword only:

- :func:`utils.oauth_url`
- :meth:`Reaction.users`

.. _migrating_2_0_event_changes:

Event Changes
-------------

- :func:`on_presence_update` replaces `on_member_update` for updates to :attr:`Member.status` and :attr:`Member.activities`.
- ``on_private_channel_create/delete`` will no longer be dispatched due to Discord changes.
- :func:`on_socket_raw_receive` is no longer dispatched for incomplete data, and the value passed is always decompressed and decoded to :class:`str`. Previously, when received a multi-part zlib-compressed binary message, :func:`on_socket_raw_receive` was dispatched on all messages with the compressed, encoded :class:`bytes`.


.. _migrating_2_0_messagetype_for_replies:

Message.type For Replies
------------------------

:attr:`Message.type` now returns :attr:`MessageType.reply` for replies, instead of :attr:`MessageType.default`.

.. _migrating_2_0_sticker_changes:

Sticker Changes
---------------

- ``Sticker.preview_image`` was removed as Discord no longer provides the data.
- ``StickerType``, an enum of sticker formats, is renamed to :class:`StickerFormatType`. Old name is used for a new enum with different purpose (checking if the sticker is guild sticker or Nitro sticker).
- :attr:`Message.stickers` is now List[:class:`StickerItem`] instead of List[:class:`Sticker`]. While :class:`StickerItem` supports some operations of previous ``Sticker``, ``description`` and ``pack_id`` attributes do not exist. :class:`Sticker` can be fetched via :meth:`StickerItem.fetch` method.
- ``Sticker.image`` is removed. :class:`Sticker` can still be fetched via :meth:`Sticker.read` or :meth:`Sticker.save` and its URL can be accessed via :attr:`Sticker.url`, just like new :class:`Emoji`.
- Due to the introduction of :class:`GuildSticker`, ``Sticker.tags`` is removed from the parent class :class:`Sticker` and moved to :attr:`StandardSticker.tags`.

.. _migrating_2_0_type_changes:

Type Changes
------------

Many method arguments now reject ``None`` or return ``None``.

- :attr:`DMChannel.recipient` is now optional, and will return ``None`` in many cases.
- :attr:`User.avatar` returns ``None`` if the avatar is not set and is instead the default avatar.
- :attr:`Guild.create_text_channel`'s ``topic`` argument no longer accepts ``None``.
- :attr:`Guild.vanity_invite` can now return ``None``.
- :attr:`Template.edit`'s ``name`` argument no longer accepts ``None``.
- :attr:`Member.edit`'s ``roles`` argument no longer accepts ``None``.
- :attr:`Bot.add_listener` and :attr:`Bot.remove_listener`'s ``name`` arguments no longer accept ``None``.
- The following :class:`.ext.commands.Context` attributes can now be ``None``: ``prefix``, ``command``, ``invoked_with``, ``invoked_subcommand``.
- :attr:`ext.commands.Command.help` can now be ``None``.

.. _migrating_2_0_miscellaneous_changes:

Miscellaneous Changes
---------------------

The following were removed:

- ``Client.request_offline_members``
- ``Client.logout``
- ``ExtensionNotFound.original``
- ``MemberCacheFlags.online``
- ``guild_subscriptions`` argument of :class:`Client`
- ``fetch_offline_members`` argument of :class:`Client`
- ``HelpCommand.clean_prefix`` moved to :attr:`ext.commands.Context.clean_prefix`
- ``VerificationLevel.table_flip`` (alias of ``high``) was removed. ``extreme``, ``very_high``, and ``double_table_flip`` attributes were removed and replaced with :attr:`VerificationLevel.highest`.

The following were renamed:

- :attr:`Colour.blurple` is renamed to :attr:`Colour.og_blurple`, and :attr:`Colour.blurple` now returns the newer color.
- ``missing_perms`` arguments and attributes of :class:`ext.commands.MissingPermissions` and :class:`ext.commands.BotMissingPermissions` are renamed to ``missing_permissions``.

The following were changed in behavior:

- :class:`Embed` that has a value is always considered truthy. Previously it only considered text fields.
- :meth:`Bot.add_cog` now raises an error when a cog with the same name is already registered. ``override`` argument can be used to bring back the 1.x behavior.
- :meth:`StageChannel.edit` can no longer edit ``topic``. Use :meth:`StageInstance.edit` instead.
- :meth:`StageChannel.clone` no longer clones its topic.

The following were changed in types:

- :attr:`ext.commands.Command.clean_params` is now a :class:`dict`, not :class:`OrderedDict`.
- ``Reaction.custom_emoji`` is now :attr:`Reaction.is_custom_emoji` for consistency.
- :attr:`IntegrationAccount.id` is now :class:`str`, instead of :class:`int`, due to Discord changes.
- :attr:`AuditLogDiff.type` is now Union[:class:`ChannelType`, :class:`StickerType`], instead of :class:`ChannelType`.

Parting Words
-------------

The v2.0 of the library implemented a lot of new features. To implement newer features, such as slash commands, they can be seen on our :resource:`guide <guide>`.
