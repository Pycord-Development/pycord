:orphan:

.. currentmodule:: discord

.. _intro:

Установка Pycord
=================

Это документация к Pycord, библиотеке для Python чтобы помощь
в создании приложений, использующих Discord API

Требования
-------------

Pycord работает с Python 3.8 или выше. Поддержка более ранних версий Python
не предусмотрена. Python 2.7 и ниже не поддерживается. Python 3.7 и ниже не поддерживается.


.. _installing:

Установка
-----------

.. note::

    Для новых функций, таких как слэш-команды, кнопки, модальные окна и потоки, вам придется установить предварительное релиза версии 2.0. ::

        python3 -m pip install -U py-cord --pre

    Для пользователей Windows, эта команда должна быть использована для установки предварительной версии: ::

        py -3 -m pip install -U py-cord --pre

Вы можете получить Pycord напрямую через PyPI: ::

    python3 -m pip install -U py-cord

Если вы используете Windows, то команда должна выглядеть так: ::

    py -3 -m pip install -U py-cord


To install additional packages for speedup,  you should use ``py-cord[speed]`` instead of ``py-cord``, e.g.
Для установки дополнительных пакетов для ускорения,  вы должны использовать ``py-cord[speed]`` вместо ``py-cord``, например:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "py-cord[speed]"

    # Windows
    py -3 -m pip install -U py-cord[speed]


Чтобы получить поддержку голосового чата, вы должны использовать ``py-cord[voice]`` вместо ``py-cord``, например: ::

    python3 -m pip install -U py-cord[voice]

Для установки поддержки голосового чата на системе Linux вам нужно установить следующее:

- `libffi <https://github.com/libffi/libffi>`_
- `libnacl <https://github.com/saltstack/libnacl>`_
- `python3-dev <https://packages.debian.org/python3-dev>`_

Для систем, основанных на Debian вам нужно установить следующее:

.. code-block:: shell

    $ apt install libffi-dev libnacl-dev python3-dev

Не забудьте проверить права доступа!

Виртуальные среды
~~~~~~~~~~~~~~~~~~~~

Иногда вы захотите избежать того, чтобы библиотеки не загрязняли вашу систему, или вы хотите использовать
другую версию библиотеки, которая уже установлена. А может вы не имеете прав чтобы установить библиотеки сразу в систему.
Для этого в Python 3.3 появилась новая функция, названная "Виртуальные Среды", чтобы помощь в решении указанных проблем.

Более углубленное изучение виртуальных сред можно найти здесь: :doc:`py:tutorial/venv`.

В кратце:

1. Идем в папку нашего проекта

    .. code-block:: shell

        $ cd your-bot-source
        $ python3 -m venv bot-env

2. Активируем виртуальную среду:

    .. code-block:: shell

        $ source bot-env/bin/activate

    Если вы используете Windows:

    .. code-block:: shell

        $ bot-env\Scripts\activate.bat

3. Дальше используйте pip как обычно:

    .. code-block:: shell

        $ pip install -U py-cord

Поздравляем. Теперь у вас есть настроенная виртуальная среда.

Основы
--------------

Pycord держится на основе событий.
Событие это то, что вы прослушиваете и затем отвечаете на него. Например, когда вы получаете
сообщение, вы получаете событие о нем, на которое вы можете ответить.

Быстрый пример того, как это работает:

.. code-block:: python3

    import discord

    class MyClient(discord.Client):
        async def on_ready(self):
            print(f'Logged on as {self.user}!')

        async def on_message(self, message):
            print(f'Message from {message.author}: {message.content}')

    client = MyClient()
    client.run('токен вашего бота')
