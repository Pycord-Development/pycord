.. _discord_api_abcs:

Abstract Base Classes
=====================

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.
They are mainly there for usage with :func:`isinstance` and :func:`issubclass`\.

This library has a module related to abstract base classes, in which all the ABCs are subclasses of
:class:`typing.Protocol`.

Snowflake
---------

.. attributetable:: discord.abc.Snowflake

.. autoclass:: discord.abc.Snowflake()
    :members:

User
----

.. attributetable:: discord.abc.User

.. autoclass:: discord.abc.User()
    :members:

PrivateChannel
--------------

.. attributetable:: discord.abc.PrivateChannel

.. autoclass:: discord.abc.PrivateChannel()
    :members:

GuildChannel
------------

.. attributetable:: discord.abc.GuildChannel

.. autoclass:: discord.abc.GuildChannel()
    :members:

Messageable
-----------

.. attributetable:: discord.abc.Messageable

.. autoclass:: discord.abc.Messageable()
    :members:
    :exclude-members: history, typing

    .. automethod:: discord.abc.Messageable.history
        :async-for:

    .. automethod:: discord.abc.Messageable.typing
        :async-with:

Connectable
-----------

.. attributetable:: discord.abc.Connectable

.. autoclass:: discord.abc.Connectable()
