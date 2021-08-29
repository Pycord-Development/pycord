pycord
==========

.. image:: https://discord.com/api/guilds/681882711945641997/embed.png
   :target: https://discord.gg/dK2qkEJ37N
   :alt: Discordサーバーの招待
.. image:: https://img.shields.io/pypi/v/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPIのバージョン情報
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPIのサポートしているPythonのバージョン

discord.pyのフォーク。 PyCordはPythonで記述されたDiscord用の最新の使いやすい機能豊富な非同期対応APIラッパーです。

主な特徴
-------------

-  ``async`` と ``await`` を使用する最新のPythonicAPI。
- 適切なレート制限の処理。
- 速度とメモリの両方で最適化されています。

インストール
----------

**Python 3.8 以降のバージョンが必須です**

完全な音声サポートなしでライブラリをインストールする場合は次のコマンドを実行してください:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U py-cord

    # Windows
    py -3 -m pip install -U py-cord

音声サポートが必要なら、次のコマンドを実行しましょう:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[voice]"

    # Windows
    py -3 -m pip install -U py-cord[voice]


開発版をインストールしたいのならば、次の手順に従ってください:
.. code:: sh

    $ git clone https://github.com/Pycord-Development/pycord
    $ cd pycord
    $ python3 -m pip install -U .[voice]


オプションパッケージ
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (音声サポート用)

Linuxで音声サポートを導入するには、前述のコマンドを実行する前にお気に入りのパッケージマネージャー(例えば ``apt`` や ``dnf`` など)を使って以下のパッケージをインストールする必要があります:

* libffi-dev (システムによっては ``libffi-devel``)
* python-dev (例えばPython 3.6用の ``python3.6-dev``)

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

examplesディレクトリに更に多くのサンプルがあります。

リンク
------

- `ドキュメント <https://pycord.readthedocs.io/en/latest/index.html>`_
- `公式Discordサーバー <https://discord.gg/dK2qkEJ37N>`_
- `Discord API <https://discord.gg/discord-api>`_
