Pycord
======

.. image:: https://img.shields.io/discord/881207955029110855?color=blue&label=discord
   :target: https://pycord.dev/discord
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI supported Python versions
.. image:: https://img.shields.io/pypi/dm/py-cord?color=blue
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI downloads

A fork of discord.py. Pycord is a modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

What Happened to Discord.py?
----------------------------
Rapptz, also known as Danny, the maintainer and core developer of discord.py will no longer be updating it. Here's his `Full explanation <https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1>`__ and an `FAQ <https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1#FAQ>`__.


Pycord v1.7.3 is the same as discord.py v1.7.3, however, Pycord v2.0 will support newer features of the API such as slash commands, context menus, scheduled events, timeouts, and others.

Key Features
------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised for both speed and memory usage.
- Full Application Command Support

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

To install additional packages for speedup, run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[speed]"
    # Windows
    py -3 -m pip install -U py-cord[speed]


To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord
    $ cd pycord
    $ python3 -m pip install -U .[voice]


Optional Packages
~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)
* `aiodns <https://pypi.org/project/aiodns/>`__, `brotlipy <https://pypi.org/project/brotlipy/>`__, `cchardet <https://pypi.org/project/cchardet/>`__ (for aiohttp speedup)
* `orjson <https://pypi.org/project/orjson/>`__ (for json speedup)

Please note that while installing voice support on Linux, you must install the following packages via your preferred package manager (e.g. ``apt``, ``dnf``, etc) BEFORE running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.10-dev`` for Python 3.10)

Quick Example
-------------

.. code:: py

    import discord

    bot = discord.Bot()

    @bot.slash_command()
    async def hello(ctx, name: str = None):
        name = name or ctx.author.name
        await ctx.respond(f"Hello {name}!")

    @bot.user_command(name="Say Hello")
    async def hi(ctx, user):
        await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")

    bot.run("token")

Traditional Commands Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    bot = commands.Bot(command_prefix=">")

    @bot.command()
    async def ping(ctx):
        await ctx.send("pong")

    bot.run("token")

You can find more examples in the examples directory.

Note: Make sure you do not reveal your bot token to anyone, it can grant access to your bot.

Links
-----

- `Documentation <https://docs.pycord.dev/en/master/index.html>`_
- `Our Official Discord Server <https://pycord.dev/discord>`_
- `Official Discord Developers Server <https://discord.gg/discord-developers>`_
- `Unofficial Discord API Server <https://discord.gg/discord-api>`_
