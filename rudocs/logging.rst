:orphan:

.. versionadded:: 0.6.0
.. _logging_setup:

Настройка логгера
==================


*Pycord* регистрирует ошибки и отладочную информацию через python :mod:`logging`
модуль. Настоятельно рекомендуется, чтобы модуль протоколирования был
так как если он не настроен, ошибки и предупреждения выводиться не будут.
Конфигурация модуля ``logging`` проста::

    import logging

    logging.basicConfig(level=logging.INFO)

Размещается в начале приложения. Это позволит выводить журналы из
discord, а также других библиотек, использующих модуль ``logging``.
непосредственно в консоль.

Необязательный аргумент ``level`` указывает, на каком уровне регистрировать события.
и может быть любым из ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO``, и
``DEBUG``, а если не указан, то по умолчанию принимает значение ``WARNING``.

Более сложные настройки возможны с помощью модуля :mod:`logging`. Для
например, для записи логов в файл с именем ``discord.log`` вместо
выводить их в консоль, можно использовать следующее::

    import discord
    import logging

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

Это рекомендуется, особенно на таких уровнях, как ``INFO`` и ``DEBUG``.
и ``DEBUG``, так как регистрируется много событий, и это засоряет
вывод вашей программы.



Для получения дополнительной информации ознакомьтесь с документацией и учебником по
:mod:`logging`.
