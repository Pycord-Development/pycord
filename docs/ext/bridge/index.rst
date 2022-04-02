.. _discord_ext_bridge:

``discord.ext.bridge`` -- A module that bridges slash commands to prefixed commands
===================================================================================

.. versionadded:: 2.0

This module allows using one command callback in order to make both a prefix command and a slash command.

.. note::
    ``ext.bridge`` requires message content intent to be enabled in order to use it.

Example usage:

.. code-block:: python3

    import discord
    from discord.ext import bridge

    bot = bridge.Bot(command_prefix="!")

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