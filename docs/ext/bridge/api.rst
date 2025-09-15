.. currentmodule:: discord

API Reference
=============

The reference manual that follows details the API of Pycord's bridge command extension module.

.. note::

    Using the prefixed command version (which uses the ``ext.commands`` extension) of bridge
    commands in guilds requires :attr:`Intents.message_context` to be enabled.


.. _ext_bridge_api:

Bots
----

Bot
~~~

.. attributetable:: discord.ext.bridge.Bot

.. autoclass:: discord.ext.bridge.Bot
    :members:

    .. automethod:: Bot.add_bridge_command()

    .. automethod:: Bot.bridge_command()
        :decorator:

    .. automethod:: Bot.bridge_group()
        :decorator:

AutoShardedBot
~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.AutoShardedBot

.. autoclass:: discord.ext.bridge.AutoShardedBot
    :members:

Event Reference
---------------

These events function similar to :ref:`the regular events <discord-api-events>`, except they
are custom to the bridge extension module.

.. function:: discord.ext.bridge.on_bridge_command_error(ctx, error)

    An error handler that is called when an error is raised
    inside a command either through user input error, check
    failure, or an error in your own code.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: discord.ext.bridge.on_bridge_command(ctx)

    An event that is called when a command is found and is about to be invoked.

    This event is called regardless of whether the command itself succeeds via
    error or completes.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: discord.ext.bridge.on_bridge_command_completion(ctx)

    An event that is called when a command has completed its invocation.

    This event is called only if the command succeeded, i.e. all checks have
    passed and users input them correctly.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

Commands
--------

BridgeCommand
~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeCommand

.. autoclass:: discord.ext.bridge.BridgeCommand
    :members:

BridgeCommandGroup
~~~~~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeCommandGroup

.. autoclass:: discord.ext.bridge.BridgeCommandGroup
    :members:

Decorators
~~~~~~~~~~
.. automethod:: discord.ext.bridge.bridge_command()
    :decorator:

.. automethod:: discord.ext.bridge.bridge_group()
    :decorator:

.. automethod:: discord.ext.bridge.map_to()
    :decorator:

.. automethod:: discord.ext.bridge.guild_only()
    :decorator:

.. automethod:: discord.ext.bridge.is_nsfw()
    :decorator:

.. automethod:: discord.ext.bridge.has_permissions()
    :decorator:

Command Subclasses
~~~~~~~~~~~~~~~~~~

.. autoclass:: discord.ext.bridge.BridgeExtCommand

.. autoclass:: discord.ext.bridge.BridgeExtGroup

.. autoclass:: discord.ext.bridge.BridgeSlashCommand

.. autoclass:: discord.ext.bridge.BridgeSlashGroup

Context
-------

BridgeContext
~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeContext

.. autoclass:: discord.ext.bridge.BridgeContext
    :members:
    :exclude-members: _respond, _defer, _edit, _get_super

BridgeContext Subclasses
~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeApplicationContext

.. autoclass:: discord.ext.bridge.BridgeApplicationContext
    :members:

.. attributetable:: discord.ext.bridge.BridgeExtContext

.. autoclass:: discord.ext.bridge.BridgeExtContext
    :members:

.. attributetable:: discord.ext.bridge.Context

.. autoclass:: discord.ext.bridge.Context

    Alias of :data:`typing.Union` [ :class:`.BridgeExtContext`, :class:`.BridgeApplicationContext` ] for typing convenience.

Options
-------

Shortcut Decorators
~~~~~~~~~~~~~~~~~~~
.. autofunction:: discord.ext.bridge.bridge_option
    :decorator:

Objects
~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeOption

.. autoclass:: discord.ext.bridge.BridgeOption
    :members:
