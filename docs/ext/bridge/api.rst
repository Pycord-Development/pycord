.. currentmodule:: discord

API Reference
==============

The reference manual that follows details the API of Pycord's bridge command extension module.

.. note::

    Using the prefixed command version (which uses the ``ext.commands`` extension) of bridge
    commands in guilds requires :attr:`Intents.message_context` to be enabled.


.. _ext_bridge_api:

Bots
-----

Bot
~~~~

.. attributetable:: discord.ext.bridge.Bot

.. autoclass:: discord.ext.bridge.Bot
    :members:

    .. automethod:: Bot.add_bridge_command()

    .. automethod:: Bot.bridge_command()
        :decorator:

    .. automethod:: Bot.bridge_group()
        :decorator:

AutoShardedBot
~~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.AutoShardedBot

.. autoclass:: discord.ext.bridge.AutoShardedBot
    :members:

Commands
---------

BridgeCommand
~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeCommand

.. autoclass:: discord.ext.bridge.BridgeCommand
    :members:

.. automethod:: discord.ext.bridge.bridge_command()
    :decorator:

BridgeCommandGroup
~~~~~~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeCommandGroup

.. autoclass:: discord.ext.bridge.BridgeCommandGroup
    :members:

.. automethod:: discord.ext.bridge.bridge_group()
    :decorator:

.. automethod:: discord.ext.bridge.map_to()
    :decorator:

Command Subclasses
~~~~~~~~~~~~~~~~~~~

.. autoclass:: discord.ext.bridge.BridgeExtCommand

.. autoclass:: discord.ext.bridge.BridgeExtGroup

.. autoclass:: discord.ext.bridge.BridgeSlashCommand

.. autoclass:: discord.ext.bridge.BridgeSlashGroup

Context
--------

BridgeContext
~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeContext

.. autoclass:: discord.ext.bridge.BridgeContext
    :members:
    :exclude-members: _respond, _defer, _edit, _get_super

BridgeContext Subclasses
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeApplicationContext

.. autoclass:: discord.ext.bridge.BridgeApplicationContext
    :members:

.. attributetable:: discord.ext.bridge.BridgeExtContext

.. autoclass:: discord.ext.bridge.BridgeExtContext
    :members:
