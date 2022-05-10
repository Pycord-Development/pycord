.. _discord_ext_bridge:

``discord.ext.bridge`` -- A module that bridges slash commands to prefixed commands
===================================================================================

.. versionadded:: 2.0

This module allows using one command callback in order to make both a prefix command and a slash command.
This page includes the API reference/documentation for the module, but only contains a short example. For a more
detailed guide on how to use this, see our `discord.ext.bridge guide <https://guide.pycord.dev/extensions/bridge>`_.

.. note::
    ``ext.bridge`` requires the message content intent to be enabled, as it uses the ``ext.commands`` extension.

Example usage:

.. code-block:: python3

    import discord
    from discord.ext import bridge

    intents = discord.Intents.default()
    intents.message_content = True

    bot = bridge.Bot(command_prefix="!", intents=intents)

    @bot.bridge_command()
    async def hello(ctx):
        await ctx.respond("Hello!")

    @bot.bridge_command()
    async def bye(ctx):
        await ctx.respond("Bye!")

    @bot.bridge_command()
    async def sum(ctx, first: int, second: int):
        s = first + second
        await ctx.respond(f"{s}")

    bot.run("TOKEN")

.. _discord_ext_bridge_api:

API Reference
-------------

Bots
~~~~

.. attributetable:: discord.ext.bridge.Bot

.. autoclass:: discord.ext.bridge.Bot
    :members:

    .. automethod:: Bot.add_bridge_command()

    .. automethod:: Bot.bridge_command()
        :decorator:

.. attributetable:: discord.ext.bridge.AutoShardedBot

.. autoclass:: discord.ext.bridge.AutoShardedBot
    :members:

    .. automethod:: Bot.add_bridge_command()

    .. automethod:: Bot.bridge_command()
        :decorator:

Commands
~~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeCommand

.. autoclass:: discord.ext.bridge.BridgeCommand
    :members:

.. automethod:: discord.ext.bridge.bridge_command()
    :decorator:

.. autoclass:: discord.ext.bridge.BridgeExtCommand
    :members:

.. autoclass:: discord.ext.bridge.BridgeSlashCommand
    :members:

Context
~~~~~~~

.. attributetable:: discord.ext.bridge.BridgeContext

.. autoclass:: discord.ext.bridge.BridgeContext
    :members:
    :exclude-members: _respond, _defer, _edit, _get_super

.. attributetable:: discord.ext.bridge.BridgeApplicationContext

.. autoclass:: discord.ext.bridge.BridgeApplicationContext
    :members:

.. attributetable:: discord.ext.bridge.BridgeExtContext

.. autoclass:: discord.ext.bridge.BridgeExtContext
    :members: