"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from discord import abc
    from discord.client import Client
    from discord.raw_models import (
        RawVoiceServerUpdateEvent,
        RawVoiceStateUpdateEvent,
    )

    P = ParamSpec("P")
    R = TypeVar("R")

ClientT = TypeVar("ClientT", bound="Client", covariant=True)

__all__ = ("VoiceProtocol",)


class VoiceProtocol(Generic[ClientT]):
    """A class that represents the Discord voice protocol.

    .. warning::

        If you are an end user, you **should not construct this manually** but instead
        take it from the return type in :meth:`abc.Connectable.connect <VoiceChannel.connect>`.
        The parameters and methods being documented here is so third party libraries can refer to it
        when implementing their own VoiceProtocol types.

    This is an abstract class. The library provides a concrete implementation
    under :class:`VoiceClient`.

    This class allows you to implement a protocol to allow for an external
    method of sending voice, such as Lavalink_ or a native library implementation.

    These classes are passed to :meth:`abc.Connectable.connect <VoiceChannel.connect>`.

    .. _Lavalink: https://github.com/freyacodes/Lavalink

    Parameters
    ----------
    client: :class:`Client`
        The client (or its subclasses) that started the connection request.
    channel: :class:`abc.Connectable`
        The voice channel that is being connected to.
    """

    def __init__(self, client: ClientT, channel: abc.Connectable) -> None:
        self.client: ClientT = client
        self.channel: abc.Connectable = channel

    async def on_voice_state_update(self, data: RawVoiceStateUpdateEvent) -> None:
        """|coro|

        A method called when the client's voice state has changed. This corresponds
        to the ``VOICE_STATE_UPDATE`` event.

        Parameters
        ----------
        data: :class:`RawVoiceStateUpdateEvent`
            The voice state payload.

            .. versionchanged:: 2.7
                This now gets passed a `RawVoiceStateUpdateEvent` object instead of a :class:`dict`, but
                accessing keys via ``data[key]`` or ``data.get(key)`` is still supported, but deprecated.
        """
        raise NotImplementedError

    async def on_voice_server_update(self, data: RawVoiceServerUpdateEvent) -> None:
        """|coro|

        A method called when the client's intially connecting to voice. This corresponds
        to the ``VOICE_SERVER_UPDATE`` event.

        Parameters
        ----------
        data: :class:`RawVoiceServerUpdateEvent`
            The voice server payload.

            .. versionchanged:: 2.7
                This now gets passed a `RawVoiceServerUpdateEvent` object instead of a :class:`dict`, but
                accessing keys via ``data[key]`` or ``data.get(key)`` is still supported, but deprecated.
        """
        raise NotImplementedError

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """|coro|

        A method called to initialise the connection.

        The library initialises this class and calls ``__init__``, and then :meth:`connect` when attempting
        to start a connection to the voice. If an error ocurrs, it calls :meth:`disconnect`, so if you need
        to implement any cleanup, you should manually call it in :meth:`disconnect` as the library will not
        do so for you.

        Within this method, to start the voice connection flow, it is recommened to use :meth:`Guild.change_voice_state`
        to start the flow. After which :meth:`on_voice_server_update` and :meth:`on_voice_state_update` will be called,
        although this could vary and cause unexpected behaviour, but that falls under Discord's way of handling the voice
        connection.

        Parameters
        ----------
        timeout: :class:`float`
            The timeout for the connection.
        reconnect: :class:`bool`
            Whether reconnection is expected.
        """
        raise NotImplementedError

    async def disconnect(self, *, force: bool) -> None:
        """|coro|

        A method called to terminate the voice connection.

        This can be either called manually when forcing a disconnection, or when an exception in :meth:`connect` ocurrs.

        It is recommended to call :meth:`cleanup` here.

        Parameters
        ----------
        force: :class:`bool`
            Whether the disconnection was forced.
        """

    def cleanup(self) -> None:
        """This method *must* be called to ensure proper clean-up during a disconnect.

        It is advisable to call this from within :meth:`disconnect` when you are completely
        done with the voice protocol instance.

        This method removes it from the internal state cache that keeps track of the currently
        alive voice clients. Failure to clean-up will cause subsequent connections to report that
        it's still connected.

        **The library will NOT automatically call this for you**, unlike :meth:`connect` and :meth:`disconnect`.
        """
        key, _ = self.channel._get_voice_client_key()
        self.client._connection._remove_voice_client(key)
