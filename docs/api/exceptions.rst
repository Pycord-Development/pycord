.. currentmodule:: discord

Exceptions
==========

Exception Hierarchy
-------------------

.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`DiscordException`
            - :exc:`ClientException`
                - :exc:`InvalidData`
                - :exc:`InvalidArgument`
                - :exc:`LoginFailure`
                - :exc:`ConnectionClosed`
                - :exc:`PrivilegedIntentsRequired`
                - :exc:`InteractionResponded`
            - :exc:`NoMoreItems`
            - :exc:`GatewayNotFound`
            - :exc:`HTTPException`
                - :exc:`Forbidden`
                - :exc:`NotFound`
                - :exc:`DiscordServerError`
            - :exc:`ApplicationCommandError`
                - :exc:`CheckFailure`
                - :exc:`ApplicationCommandInvokeError`
            - :exc:`ExtensionError`
                - :exc:`ExtensionAlreadyLoaded`
                - :exc:`ExtensionNotLoaded`
                - :exc:`NoEntryPointError`
                - :exc:`ExtensionFailed`
                - :exc:`ExtensionNotFound`
            - :exc:`sinks.SinkException`
                - :exc:`sinks.RecordingException`
                - :exc:`sinks.WaveSinkError`
                - :exc:`sinks.MP3SinkError`
                - :exc:`sinks.MP4SinkError`
                - :exc:`sinks.M4ASinkError`
                - :exc:`sinks.MKVSinkError`
                - :exc:`sinks.MKASinkError`
                - :exc:`sinks.OGGSinkError`

Objects
-------

The following exceptions are thrown by the library.

.. autoexception:: DiscordException

.. autoexception:: ClientException

.. autoexception:: LoginFailure

.. autoexception:: NoMoreItems

.. autoexception:: HTTPException
    :members:

.. autoexception:: Forbidden

.. autoexception:: NotFound

.. autoexception:: DiscordServerError

.. autoexception:: InvalidData

.. autoexception:: InvalidArgument

.. autoexception:: GatewayNotFound

.. autoexception:: ConnectionClosed

.. autoexception:: PrivilegedIntentsRequired

.. autoexception:: InteractionResponded

.. autoexception:: discord.opus.OpusError

.. autoexception:: discord.opus.OpusNotLoaded

.. autoexception:: discord.ApplicationCommandError
    :members:

.. autoexception:: discord.CheckFailure
    :members:

.. autoexception:: discord.ApplicationCommandInvokeError
    :members:

.. autoexception:: discord.ExtensionError
    :members:

.. autoexception:: discord.ExtensionAlreadyLoaded
    :members:

.. autoexception:: discord.ExtensionNotLoaded
    :members:

.. autoexception:: discord.NoEntryPointError
    :members:

.. autoexception:: discord.ExtensionFailed
    :members:

.. autoexception:: discord.ExtensionNotFound
    :members:

.. autoexception:: discord.sinks.SinkException

.. autoexception:: discord.sinks.RecordingException

.. autoexception:: discord.sinks.WaveSinkError

.. autoexception:: discord.sinks.MP3SinkError

.. autoexception:: discord.sinks.MP4SinkError

.. autoexception:: discord.sinks.M4ASinkError

.. autoexception:: discord.sinks.MKVSinkError

.. autoexception:: discord.sinks.MKASinkError

.. autoexception:: discord.sinks.OGGSinkError
