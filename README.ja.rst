pycord
==========

.. image:: https://discord.com/api/guilds/881207955029110855/embed.png
   :target: https://pycord.dev/discord
   :alt: Discordサーバーの招待
.. image:: https://img.shields.io/pypi/v/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPIのバージョン情報
.. image:: https://img.shields.io/pypi/pyversions/py-cord.svg
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPIのサポートしているPythonのバージョン
.. image:: https://img.shields.io/pypi/dm/py-cord?color=blue
   :target: https://pypi.python.org/pypi/py-cord
   :alt: PyPIダウンロード

discord.pyのフォークです。PyCordはPythonで書かれたDiscordのモダンで使いやすく、豊富な機能を持ち、非同期に対応したAPIラッパーです。

主な特徴
-------------

- ``async`` と ``await`` を使ったモダンなPythonらしいAPI。
- 適切なレート制限の処理。
- 速度とメモリ使用量の両方が最適化されています。
- スラッシュコマンド、コンテキストメニュー、メッセージコンポーネントをサポート。

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

なお、Linuxで音声サポートをインストールする場合は、上記のコマンドを実行する前に、お好みのパッケージマネージャー（apt、dnfなど）を使って以下のパッケージをインストールしておく必要があります。

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

その他の例は、examples ディレクトリにあります。

注意： ボットトークンを誰にも見せないようにしてください。

リンク
------

- `ドキュメント <https://docs.pycord.dev/en/master/index.html>`_
- `公式Discordサーバー <https://pycord.dev/discord>`_
- `Discord開発者 <https://discord.gg/discord-developers>`_
- `Discord API <https://discord.gg/discord-api>`_
