.. currentmodule:: discord.ext.ipc

Working with `Server` processes
===============================
The :class:`Server` process sends data to the :class:`Session`, while being in separate IP's

Sending data
------------
To sending data you will want to use the :meth:`Server.route` like so:

.. code-block:: py

    from discord.ext import ipc, commands

    bot = commands.Bot(...)
    server = ipc.Server(bot, ...)
    
    @server.route()
    async def give_guild_categories(data):
        guild = bot.get_guild(data.guild_id) # get the guild.

        return guild.categories # gives the categories in the guild

and vice versa with anything else sent.