.. currentmodule:: discord

.. _migrating_pycord:

Migrating to 2.0
=================

The full change list of 2.0


Significant Changes
-------------------

- `on_socket_response` Was Removed


Webhook
-------
Webhooks in discord.py V2 have been overhauled 

`webhook_update` now uses guild info from the gateway



User API
--------

Anything allowing you to Use user Account's have been removed 

The following Classes Were Deleted in addendum

``Profile``, ``Relationship``, ``CallMessage``, ``GroupCall``,

``RelationshipType``, ``HypeSquadHouse```, ``PremiumType``, ``UserContentFilter``, ``FriendFlags``, ``Theme``,

``GroupChannel.add_recipients``, ``remove_recipients``

``Guild.ack``

``Client.fetch_user_profile``

``Message.call`` & ``ack``

``ClientUser.email``, ``premium``, ``premium_type``, ``get_relationship``, ``relationships```, ``friends``, ``blocked``, ``create_group``, ``edit_settings``

Every ``ClientUser.edit()`` ``password``, ``new_password``, ``email``, ``house arguments``

``User.relationship``, ``mutual_friends``, ``is_friend``, ``is_blocked``, ``block``, ``unblock``, ``remove_friend``, ``send_friend_request``, ``profile``


SpeedUps
--------
The library has significantly improved in speed since v1.7.x
Some Speed results are shown below:

+-------------------------------+----------------------------------+----------------------------------+
|             Testsetup         |          boot up before          |            boot up now           |
+-------------------------------+----------------------------------+----------------------------------+
| 735 guilds (with chunking)    | 57s/1.7 GiB RAM                  | 42s/1.4 GiB RAM                  |
+-------------------------------+----------------------------------+----------------------------------+
| 27k guilds (with chunking)    | 477s/8 GiB RAM                   | 303s/7.2 GiB                     |
+-------------------------------+----------------------------------+----------------------------------+
| 48k guilds (without chunking) | 109s                             | 67s                              |
+-------------------------------+----------------------------------+----------------------------------+
| 106k guilds (without chunking)| 3300s                            | 3090s                            |
+-------------------------------+----------------------------------+----------------------------------+

.. note::
    
    Performance May Differ with Computer/Server specs and location

- The public API is completely type-hinted
- Most ``edit`` methods now return their updated counterpart rather than doing an in-place edit

Miscellaneous
-------------