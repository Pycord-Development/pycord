.. pycord documentation master file, created by
   sphinx-quickstart on Fri Aug 21 05:43:30 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Добро пожаловать в документацию Pycord!
=================

.. image:: /images/snake.svg
.. image:: /images/snake_dark.svg

Pycord - это современный, простой, богатый по функционалу, асинхронный инструмент
для взаимодествия с API Discord.

**Особенности:**

- Современное использование ``async``\/``await`` синтаксиса
- Умная обработка рейт лимита не превышающая 429с
- Дополнение команд для удобного создания ботов
- Прост в использовании в ООП стиле
- Оптимизирован под скорость и память

Начинаем!
-----------------

Вы впервые пишите ботов с Pycord? Это отличное место чтобы начать!

- **Первые шаги:** :doc:`installing` | :doc:`quickstart` | :doc:`logging` | :resource:`Guide <guide>`
- **Работа с Discord:** :doc:`discord` | :doc:`intents`
- **Примеры:** Многие примеры можно найти в :resource:`repository <examples>`.

Помощь
--------------

Если у вас проблемы с чем-либо, здесь вы сможете найти ответ на вопрос:

- Попробуйте изучить :doc:`faq`, здесь есть большинство ответов на вопросы.
- Вы можете спросить о чем-либо на нашем сервере: :resource:`Discord <discord>` .
- Если вы ищите что-то конкретное - попробуйте :ref:`index <genindex>` или :ref:`searching <search>`.
- Сообщить о баге можно в :resource:`issue tracker <issues>`.
- Спросить можно также тут :resource:`GitHub discussions page <discussions>`.

Расширения
------------

Эти расширения помогут вам во время разработки, когда речь идет об обычных задачах.

.. toctree::
  :maxdepth: 1

  ext/commands/index.rst
  ext/tasks/index.rst
  ext/pages/index.rst
  ext/bridge/index.rst

Руководства
---------

На этих страницах подробно описано все, что может делать API.

.. toctree::
  :maxdepth: 1

  api
  discord.ext.commands API Reference <ext/commands/api.rst>
  discord.ext.tasks API Reference <ext/tasks/index.rst>
  discord.ext.pages API Reference <ext/pages/index.rst>
  discord.ext.bridge API Reference <ext/bridge/index.rst>

Информация
------

Если вы ищите что-то, что связанно с Pycord - вы можете найти это здесь.

.. toctree::
  :maxdepth: 1

  whats_new
  version_guarantees
  migrating_to_v1
