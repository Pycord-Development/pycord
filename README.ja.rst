pycord
==========

.. image:: https://discord.com/api/guilds/681882711945641997/embed.png
   :target: https://discord.gg/dK2qkEJ37N
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord.py
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPI supported Python versions

discord.pyのフォーク。 PyCordは、Pythonで記述されたDiscord用の最新の使いやすい機能豊富な非同期対応APIラッパーです。

主な機能
-------------

- ``async``と``await``を使用する最新のPythonicAPI。
- 適切なレート制限の処理。
- 速度とメモリの両方で最適化されています。

インストール
----------

**Python3.8以降が必要です**

音声を完全にサポートせずにライブラリをインストールするには、次のコマンドを実行するだけです。

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U py-cord

    # Windows
    py -3 -m pip install -U py-cord

それ以外の場合、音声サポートを受けるには、次のコマンドを実行する必要があります。

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[voice]"

    # Windows
    py -3 -m pip install -U py-cord[voice]


開発バージョンをインストールするには、次の手順を実行します。

.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord.py
    $ cd pycord
    $ python3 -m pip install -U .[voice]


オプションパッケージ
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (音声サポート用)

Linuxのインストール音声では、上記のコマンドを実行する前に、お気に入りのパッケージマネージャー（apt、dnfなど）を介して次のパッケージをインストールする必要があることに注意してください。

* libffi-dev (または一部のシステムでは ``libffi-devel``)
* python-dev (例： ``python3.6-dev`` Python 3.6の場合)

簡単な例
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

Botの例
~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

例のディレクトリには、さらに多くの例があります。

リンク
------

- `Documentation <https://pycord.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/dK2qkEJ37N>`_
- `Discord API <https://discord.gg/discord-api>`_
