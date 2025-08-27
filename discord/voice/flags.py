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

from discord.flags import BaseFlags, fill_with_flags, flag_value


@fill_with_flags()
class SpeakingFlags(BaseFlags):
    r"""Wraps up a Discord user speaking state flag value.

    .. container:: operations

        .. describe:: x == y

            Checks if two flags are equal.
        .. describe:: x != y

            Checks if two flags are not equal.
        .. describe:: x + y

            Adds two flags together. Equivalent to ``x | y``.
        .. describe:: x - y

            Substract two flags from each other.
        .. describe:: x | y

            Returns the union of two flags. Equivalent to ``x + y``.
        .. describe:: x & y

            Returns the intersection of two flags.
        .. describe:: ~x

            Returns the inverse of a flag.
        .. describe:: hash(x)

            Returns the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.

    .. versionadded:: 2.7

    Attributes
    ----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    @flag_value
    def voice(self):
        """:class:`bool`: Normal transmission of voice audio"""
        return 1 << 0

    @flag_value
    def soundshare(self):
        """:class:`bool`: Transmission of context audio for video, no speaking indicator"""
        return 1 << 1

    @flag_value
    def priority(self):
        """:class:`bool`: Priority speaker, lowering audio of other speakers"""
        return 1 << 2
