.. image:: https://raw.githubusercontent.com/Pycord-Development/pycord/master/pycord.png
   :alt: Pycord

Pycord is a modern, easy to use, feature-rich, and async-ready API wrapper for Discord written in Python.

.. image:: https://img.shields.io/pypi/v/py-cord.svg?style=for-the-badge&logo=pypi&color=yellowgreen&logoColor=white
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg?style=for-the-badge&logo=python&logoColor=white
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI supported Python versions
.. image:: https://img.shields.io/pypi/dm/py-cord?color=blueviolet&logo=pypi&logoColor=white&style=for-the-badge
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI downloads
.. image:: https://img.shields.io/github/v/release/Pycord-Development/pycord?include_prereleases&label=Latest%20Release&logo=github&sort=semver&style=for-the-badge&logoColor=white
   :target: https://github.com/Pycord-Development/pycord/releases
   :alt: Latest release
.. image:: https://img.shields.io/discord/881207955029110855?label=discord&style=for-the-badge&logo=discord&color=5865F2&logoColor=white
   :target: https://pycord.dev/discord
   :alt: Discord server invite
.. image:: https://img.shields.io/github/sponsors/Pycord-Development?style=for-the-badge
   :target: https://github.com/sponsors/Pycord-Development
   :alt: GitHub Sponsors

Key Features
------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised for both speed and memory usage.
- Full application API support.

Installing
----------

**Pycord supports Python 3.10 - 3.14.**

To install the base library, run the following command:

.. code:: sh

    # Linux/macOS
    $ python3 -m pip install -U py-cord

    # Windows
    $ py -3 -m pip install -U py-cord

Otherwise, to install optional packages for full voice support or speedup,
run the following command(s):

.. code:: sh

    # Linux/macOS
    $ python3 -m pip install -U "py-cord[voice]"
    $ python3 -m pip install -U "py-cord[speed]"

    # Windows
    $ py -3 -m pip install -U py-cord[voice]
    $ py -3 -m pip install -U py-cord[speed]

To clone and install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord
    $ cd pycord
    $ python3 -m pip install -U .

Or, to install the development version directly from the repository:

.. code:: sh

    # Linux/macOS
    $ python3 -m pip install "py-cord @ git+https://github.com/Pycord-Development/pycord"

    # Windows
    $ py -3 -m pip install "py-cord @ git+https://github.com/Pycord-Development/pycord"

Pycord is managed with `uv <https://docs.astral.sh/uv/>`__. If you want to contribute to Pycord, refer to
`CONTRIBUTING.md <https://github.com/Pycord-Development/pycord/blob/master/CONTRIBUTING.md>`__ for more information.

Optional Packages
~~~~~~~~~~~~~~~~~

- `davey <https://pypi.org/project/davey/>`__, `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)
- `aiodns <https://pypi.org/project/aiodns/>`__, `brotli <https://pypi.org/project/brotli/>`__ (for aiohttp speedup)
- `msgspec <https://pypi.org/project/msgspec/>`__ (for json speedup)

Please note that while installing voice support on Linux, you must install the following packages via your preferred package manager (e.g. ``apt``, ``dnf``, etc) BEFORE running the above commands:

- libffi-dev (or ``libffi-devel`` on some systems)
- python-dev (e.g. ``python3.14-dev`` for Python 3.14)

Quick Examples
--------------

Application Commands
~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import discord

    bot = discord.Bot()

    @bot.slash_command()
    async def hello(ctx, name: str | None = None):
        name = name or ctx.author.name
        await ctx.respond(f"Hello {name}!")

    @bot.user_command(name="Say Hi")
    async def hi(ctx, user: discord.User):
        await ctx.respond(f"{ctx.author.mention} says hi to {user.name}!")

    bot.run(TOKEN)

Prefix Commands
~~~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=">", intents=intents)

    @bot.command()
    async def ping(ctx):
        await ctx.send("pong")

    bot.run(TOKEN)

You can find more code examples in the `examples directory <examples/>`__.

+-----------------------------------------------------------------------------------------------------------+
| **⚠️ Warning:** Make sure you do not reveal your bot token to anyone, as it can grant access to your bot. |
+-----------------------------------------------------------------------------------------------------------+

Useful Links
------------

- `Documentation <https://docs.pycord.dev/en/master/index.html>`__
- `Official Guide <https://guide.pycord.dev>`__
- `Our Official Discord Server <https://pycord.dev/discord>`__
- `Official Discord Developers Server <https://discord.gg/discord-developers>`__
- `SonoLink, a high-performance Lavalink v4 wrapper for Python <https://github.com/sonolink/sonolink>`__

Translations
------------

.. image:: https://badges.awesome-crowdin.com/translation-200034237-5.png
   :alt: Translation Status
.. image:: https://badges.crowdin.net/badge/dark/crowdin-on-light.png
   :target: https://translations.pycord.dev/documentation/?utm_source=badge&utm_medium=referral&utm_campaign=badge-add-on
   :alt: Crowdin | Agile localization for tech companies
