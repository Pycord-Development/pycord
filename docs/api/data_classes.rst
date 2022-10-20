.. currentmodule:: discord

.. _discord_api_data:

Data Classes
============

Some classes are just there to be data containers, this lists them.

Unlike :ref:`models <discord_api_models>` you are allowed to create
most of these yourself, even if they can also be used to hold attributes.

Nearly all classes here have :ref:`py:slots` defined which means that it is
impossible to have dynamic attributes to the data classes.

The only exception to this rule is :class:`Object`, which is made with
dynamic attributes in mind.

.. attributetable:: Object

.. autoclass:: Object
    :members:

.. attributetable:: SelectOption

.. autoclass:: SelectOption
    :members:

.. attributetable:: Intents

.. autoclass:: Intents
    :members:

.. attributetable:: ShardInfo

.. autoclass:: ShardInfo()
    :members:

Message
-------

.. attributetable:: AllowedMentions

.. autoclass:: AllowedMentions
    :members:

.. attributetable:: MessageReference

.. autoclass:: MessageReference
    :members:

.. attributetable:: PartialMessage

.. autoclass:: PartialMessage
    :members:

.. attributetable:: File

.. autoclass:: File
    :members:

Embed
~~~~~

.. attributetable:: Embed

.. autoclass:: Embed
    :members:

.. attributetable:: EmbedField

.. autoclass:: EmbedField
    :members:


Flags
-----

.. attributetable:: MemberCacheFlags

.. autoclass:: MemberCacheFlags
    :members:

.. attributetable:: ApplicationFlags

.. autoclass:: ApplicationFlags
    :members:

.. attributetable:: SystemChannelFlags

.. autoclass:: SystemChannelFlags()
    :members:

.. attributetable:: MessageFlags

.. autoclass:: MessageFlags()
    :members:

.. attributetable:: PublicUserFlags

.. autoclass:: PublicUserFlags()
    :members:

.. attributetable:: ChannelFlags

.. autoclass:: ChannelFlags()
    :members:

Colour
------

.. attributetable:: Colour

.. autoclass:: Colour
    :members:

Activity
--------

.. attributetable:: Activity

.. autoclass:: Activity
    :members:

.. attributetable:: BaseActivity

.. autoclass:: BaseActivity
    :members:

.. attributetable:: Game

.. autoclass:: Game
    :members:

.. attributetable:: Streaming

.. autoclass:: Streaming
    :members:

.. attributetable:: CustomActivity

.. autoclass:: CustomActivity
    :members:

Permissions
-----------

.. attributetable:: Permissions

.. autoclass:: Permissions
    :members:

.. attributetable:: PermissionOverwrite

.. autoclass:: PermissionOverwrite
    :members:
