from __future__ import annotations

from typing_extensions import final, override

from .base import BaseFlags, fill_with_flags, flag_value


@final
@fill_with_flags(inverted=True)
class SystemChannelFlags(BaseFlags):
    r"""Wraps up a Discord system channel flag value.

    Similar to :class:`Permissions`\, the properties provided are two way.
    You can set and retrieve individual bits using the properties as if they
    were regular bools. This allows you to edit the system flags easily.

    To construct an object you can pass keyword arguments denoting the flags
    to enable or disable.

    .. container:: operations

        .. describe:: x == y

            Checks if two flags are equal.
        .. describe:: x != y

            Checks if two flags are not equal.
        .. describe:: x + y

            Adds two flags together. Equivalent to ``x | y``.
        .. describe:: x - y

            Subtracts two flags from each other.
        .. describe:: x | y

            Returns the union of two flags. Equivalent to ``x + y``.
        .. describe:: x & y

            Returns the intersection of two flags.
        .. describe:: ~x

            Returns the inverse of a flag.
        .. describe:: hash(x)

               Return the flag's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(name, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = tuple()

    # For some reason the flags for system channels are "inverted"
    # ergo, if they're set then it means "suppress" (off in the GUI toggle)
    # Since this is counter-intuitive from an API perspective and annoying
    # these will be inverted automatically

    @override
    def _has_flag(self, o: int) -> bool:
        return (self.value & o) != o

    @override
    def _set_flag(self, o: int, toggle: bool) -> None:
        if toggle:
            self.value &= ~o
        else:
            self.value |= o

    @flag_value
    def join_notifications(self):
        """:class:`bool`: Returns ``True`` if the system channel is used for member join notifications."""
        return 1

    @flag_value
    def premium_subscriptions(self):
        """:class:`bool`: Returns ``True`` if the system channel is used for "Nitro boosting" notifications."""
        return 2

    @flag_value
    def guild_reminder_notifications(self):
        """:class:`bool`: Returns ``True`` if the system channel is used for server setup helpful tips notifications.

        .. versionadded:: 2.0
        """
        return 4

    @flag_value
    def join_notification_replies(self):
        """:class:`bool`: Returns ``True`` if the system channel is allowing member join sticker replies.

        .. versionadded:: 2.0
        """
        return 8
