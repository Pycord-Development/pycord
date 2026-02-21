.. currentmodule:: discord

Sinks
=====

Core
----

.. autoclass:: discord.sinks.Sink
    :members:

.. autoclass:: discord.sinks.RawData
    :members:

.. autoclass:: discord.sinks.SinkHandler
    :members:

.. autoclass:: discord.sinks.SinkFilter
    :members:


Default Sinks
-------------

.. autoclass:: discord.sinks.WaveSink
    :members:

.. autoclass:: discord.sinks.WavSink
    :members:

.. autoclass:: discord.sinks.MP3Sink
    :members:

.. autoclass:: discord.sinks.MP4Sink
    :members:

.. autoclass:: discord.sinks.M4ASink
    :members:

.. autoclass:: discord.sinks.MKVSink
    :members:

.. autoclass:: discord.sinks.MKASink
    :members:

.. autoclass:: discord.sinks.OGGSink
    :members:

Events
------
These section outlines all the available sink events.

.. function:: on_voice_packet_receive(user, data)
    Called when a voice packet is received from a member.

    This is called **after** the filters went through.

    :param user: The user the packet is from. This can sometimes be a :class:`~discord.Object` object.
    :type user: :class:`~discord.abc.Snowflake`
    :param data: The RawData of the packet.
    :type data: :class:`~.RawData`

.. function:: on_unfiltered_voice_packet_receive(user, data)
    Called when a voice packet is received from a member.

    Unlike ``on_voice_packet_receive``, this is called **before any filters** are called.

    :param user: The user the packet is from. This can sometimes be a :class:`~discord.Object` object.
    :type user: :class:`~discord.abc.Snowflake`
    :param data: The RawData of the packet.
    :type data: :class:`~.RawData`

.. function:: on_speaking_state_update(user, before, after)
    Called when a member's voice state changes.

    This is called **after** the filters went through.

    :param user: The user which speaking state has changed. This can sometimes be a :class:`~discord.Object` object.
    :type user: :class:`~discord.abc.Snowflake`
    :param before: The user's state before it was updated.
    :type before: :class:`~discord.SpeakingFlags`
    :param after: The user's state after it was updated.
    :type after: :class:`~discord.SpeakingFlags`

.. function:: on_unfiltered_speaking_state_update(user, before, after)
    Called when a voice packet is received from a member.

    Unlike ``on_speaking_state_update``, this is called **before any filters** are called.

    :param user: The user which speaking state has changed. This can sometimes be a :class:`~discord.Object` object.
    :type user: :class:`~discord.abc.Snowflake`
    :param before: The user's state before it was updated.
    :type before: :class:`~discord.SpeakingFlags`
    :param after: The user's state after it was updated.
    :type after: :class:`~discord.SpeakingFlags`

.. function:: on_user_connect(user, channel)
    Called when a user connects to a voice channel.

    This is called **after** the filters went through.

    :param user: The user that has connected to the voice channel. This can sometimes be a :class:`~discord.Object` object.
    :type user: :class:`~discord.abc.Snowflake`
    :param channel: The channel the user has connected to. This usually resolved to the correct channel type, but if it fails
    it defaults to a :class:`~discord.Object` object.
    :type channel: :class:`~discord.abc.Snowflake`

.. function:: on_unfiltered_user_connect(user, channel)
    Called when a user connects to a voice channel.

    Unlike ``on_user_connect``, this is called **before any filters** are called.

    :param user: The user that has connected to the voice channel. This can sometimes be a :class:`~discord.Object` object.
    :type user: :class:`~discord.abc.Snowflake`
    :param channel: The channel the user has connected to. This usually resolved to the correct channel type, but if it fails
    it defaults to a :class:`~discord.Object` object.
    :type channel: :class:`~discord.abc.Snowflake`

.. function:: on_error(event, exception, \*args, \*\*kwargs)
    Called when an error ocurrs in any of the events above. The default implementation logs the exception
    to stdout.

    :param event: The event in which the error ocurred.
    :type event: :class:`str`
    :param exception: The exception that ocurred.
    :type exception: :class:`Exception`
    :param \*args: The arguments that were passed to the event.
    :param \*\*kwargs: The key-word arguments that were passed to the event.
