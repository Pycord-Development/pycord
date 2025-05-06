from __future__ import annotations

from typing import Any, ClassVar

from typing_extensions import Self, final

from .base import BaseFlags, fill_with_flags, flag_value


@final
@fill_with_flags()
class UserFlags(BaseFlags):
    """Wraps up the Discord user flags value.

    The properties provided are two way. You can set and retrieve individual
    bits using the properties as if they were regular bools.

    .. container:: operations

        .. describe:: x == y

            Checks if two flags are equal.
        .. describe:: x != y

            Checks if two flags are not equal.
        .. describe:: x <= y

            Checks if a flag is a subset of another flag.
        .. describe:: x >= y

            Checks if a flag is a superset of another flag.
        .. describe:: x < y

             Checks if a flag is a strict subset of another flag.
        .. describe:: x > y

             Checks if a flag is a strict superset of another flag.
        .. describe:: hash(x)

               Return the flag's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(flag, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.

    Attributes
    ----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 23-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    DEFAULT_VALUE: ClassVar[int] = 0

    def __init__(self, value: int = 0, **kwargs: bool) -> None:
        super().__init__(**kwargs)
        self.value: int = value

    @classmethod
    def none(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`UserFlags` with no flags set."""
        return cls(0)

    @classmethod
    def all(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`UserFlags` with all flags set."""
        return cls(0b11111111111111111111111)

    @flag_value
    def staff(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a Discord Employee."""
        return 1 << 0

    @flag_value
    def partner(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a Discord Partner."""
        return 1 << 1

    @flag_value
    def hypesquad(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a HypeSquad Events member."""
        return 1 << 2

    @flag_value
    def bug_hunter_level_1(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a Bug Hunter Level 1."""
        return 1 << 3

    @flag_value
    def hypesquad_house_bravery(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a member of House Bravery."""
        return 1 << 6

    @flag_value
    def hypesquad_house_brilliance(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a member of House Brilliance."""
        return 1 << 7

    @flag_value
    def hypesquad_house_balance(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a member of House Balance."""
        return 1 << 8

    @flag_value
    def premium_early_supporter(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is an Early Nitro Supporter."""
        return 1 << 9

    @flag_value
    def team_pseudo_user(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a team."""
        return 1 << 10

    @flag_value
    def bug_hunter_level_2(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a Bug Hunter Level 2."""
        return 1 << 14

    @flag_value
    def verified_bot(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a Verified Bot."""
        return 1 << 16

    @flag_value
    def verified_developer(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is an Early Verified Bot Developer."""
        return 1 << 17

    @flag_value
    def certified_moderator(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is a Discord Certified Moderator."""
        return 1 << 18

    @flag_value
    def bot_http_interactions(self) -> int:
        """:class:`bool`: Returns ``True`` if the bot uses only HTTP interactions and is shown in the online member list."""
        return 1 << 19

    @flag_value
    def active_developer(self) -> int:
        """:class:`bool`: Returns ``True`` if the user is an Active Developer."""
        return 1 << 22

    def is_subset(self, other: Any) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if self has the same or fewer flags as other."""
        if isinstance(other, UserFlags):
            return (self.value & other.value) == self.value
        raise TypeError(
            f"Cannot compare {self.__class__.__name__} with {other.__class__.__name__}"
        )

    def is_superset(self, other: Any) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if self has the same or more flags as other."""
        if isinstance(other, UserFlags):
            return (self.value | other.value) == self.value
        raise TypeError(
            f"Cannot compare {self.__class__.__name__} with {other.__class__.__name__}"
        )

    def is_strict_subset(
        self, other: Any
    ) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if the flags on other are a strict subset of those on self."""
        return self.is_subset(other) and self != other

    def is_strict_superset(
        self, other: Any
    ) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if the flags on other are a strict superset of those on self."""
        return self.is_superset(other) and self != other

    __le__ = is_subset
    __ge__ = is_superset
    __lt__ = is_strict_subset
    __gt__ = is_strict_superset
