from typing_extensions import final

from .base import BaseFlags, fill_with_flags, flag_value


@final
@fill_with_flags()
class RoleFlags(BaseFlags):
    r"""Wraps up the Discord Role flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two RoleFlags are equal.
        .. describe:: x != y

            Checks if two RoleFlags are not equal.
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
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = tuple()

    @flag_value
    def in_prompt(self):
        """:class:`bool`: Returns ``True`` if the role is selectable in one of the guild's :class:`~discord.OnboardingPrompt`."""
        return 1 << 0
