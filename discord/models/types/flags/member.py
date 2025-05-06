from __future__ import annotations

from typing_extensions import final

from .base import BaseFlags, fill_with_flags, flag_value


@final
@fill_with_flags()
class MemberFlags(BaseFlags):
    r"""Wraps up the Discord Member flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two MemberFlags are equal.
        .. describe:: x != y

            Checks if two MemberFlags are not equal.
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
            Note that aliases are not shown.

    .. versionadded:: 2.6

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def did_rejoin(self):
        """:class:`bool`: Returns ``True`` if the member left and rejoined the guild."""
        return 1 << 0

    @flag_value
    def completed_onboarding(self):
        """:class:`bool`: Returns ``True`` if the member has completed onboarding."""
        return 1 << 1

    @flag_value
    def bypasses_verification(self):
        """:class:`bool`: Returns ``True`` if the member is exempt from verification requirements.

        .. note::

            This can be edited through :func:`~discord.Member.edit`.
        """
        return 1 << 2

    @flag_value
    def started_onboarding(self):
        """:class:`bool`: Returns ``True`` if the member has started onboarding."""
        return 1 << 3

    @flag_value
    def is_guest(self):
        """:class:`bool`: Returns ``True`` if the member is a guest and can only access the voice channel they were invited to."""
        return 1 << 4

    @flag_value
    def started_home_actions(self):
        """:class:`bool`: Returns ``True`` if the member has started Server Guide new member actions."""
        return 1 << 5

    @flag_value
    def completed_home_actions(self):
        """:class:`bool`: Returns ``True`` if the member has completed Server Guide new member actions."""
        return 1 << 6

    @flag_value
    def automod_quarantined_username(self):
        """:class:`bool`: Returns ``True`` if the member's username, display name, or nickname is blocked by AutoMod."""
        return 1 << 7

    @flag_value
    def dm_settings_upsell_acknowledged(self):
        """:class:`bool`: Returns ``True`` if the member has dismissed the DM settings upsell."""
        return 1 << 9
