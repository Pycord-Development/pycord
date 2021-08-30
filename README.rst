pycord
==========

.. image:: https://discord.com/api/guilds/681882711945641997/embed.png
   :target: https://discord.gg/dK2qkEJ37N
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI supported Python versions

A fork of discord.py. PyCord is a modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised in both speed and memory.

Installing
----------

**Python 3.8 or higher is required**

To install the library without full voice support, you can just run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U py-cord

    # Windows
    py -3 -m pip install -U py-cord

Otherwise to get voice support you should run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[voice]"

    # Windows
    py -3 -m pip install -U py-cord[voice]


To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord
    $ cd pycord
    $ python3 -m pip install -U .[voice]


Optional Packages
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)

Please note that on Linux installing voice you must install the following packages via your favourite package manager (e.g. ``apt``, ``dnf``, etc) before running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.6-dev`` for Python 3.6)

Quick Example
--------------

.. code:: py

    import discord

    class MyClient(discord.Client):
        async def on_ready(self):
            print('Logged on as', self.user)

        async def on_message(self, message):
            # don't respond to ourselves
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

    client = MyClient()
    client.run('token')

Bot Example
~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

SlashCommand Example
~~~~~~~~~~~~~

.. code:: py
from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext

bot = Client(intents=Intents.default())
slash = SlashCommand(bot)

@slash.slash(name="test")
async def test(ctx: SlashContext):
    embed = Embed(title="Embed Test")
    await ctx.send(embed=embed)

bot.run("discord_token")

You can find more examples in the examples directory.

Links
------

- `Documentation <https://pycord.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/dK2qkEJ37N>`_
- `Discord API <https://discord.gg/discord-api>`_
