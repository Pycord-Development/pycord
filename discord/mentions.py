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

from typing import TYPE_CHECKING, Final, TypeVar, Literal

from typing_extensions import Sentinel, override

__all__ = ("AllowedMentions",)

if TYPE_CHECKING:
    from .abc import Snowflake
    from .types.message import AllowedMentions as AllowedMentionsPayload


DEFAULT_MENTIONS: Final = Sentinel("DEFAULT_MENTIONS")

A = TypeVar("A", bound="AllowedMentions")

_T = TypeVar("_T")


def _override_unless_unset(base: _T, override: _T) -> _T:
    return base if override is DEFAULT_MENTIONS else override


class AllowedMentions:
    """A class that represents what mentions are allowed in a message.

    This class can be set during :class:`Client` initialisation to apply
    to every message sent. It can also be applied on a per-message basis
    via :meth:`abc.Messageable.send` for more fine-grained control.
    """

    __slots__: tuple[str, ...] = ("_everyone", "_users", "_roles", "_replied_user")

    def __init__(
        self,
        *,
        everyone: bool | DEFAULT_MENTIONS = DEFAULT_MENTIONS,
        users: bool | list[Snowflake] | DEFAULT_MENTIONS = DEFAULT_MENTIONS,
        roles: bool | list[Snowflake] | DEFAULT_MENTIONS = DEFAULT_MENTIONS,
        replied_user: bool | DEFAULT_MENTIONS = DEFAULT_MENTIONS,
    ):
        self._everyone: bool | DEFAULT_MENTIONS = everyone
        self._users: bool | list[Snowflake] | DEFAULT_MENTIONS = users
        self._roles: bool | list[Snowflake] | DEFAULT_MENTIONS = roles
        self._replied_user: bool | DEFAULT_MENTIONS = replied_user

    @property
    def everyone(self) -> bool:
        """Whether to allow everyone and here mentions. Defaults to ``True``."""
        return self._everyone is DEFAULT_MENTIONS or self._everyone

    @everyone.setter
    def everyone(self, value: bool) -> None:
        self._everyone = value

    @property
    def users(self) -> bool | list[Snowflake]:
        """Controls the users being mentioned. If ``True`` (the default) then
        users are mentioned based on the message content. If ``False`` then
        users are not mentioned at all. If a list of :class:`abc.Snowflake`
        is given then only the users provided will be mentioned, provided those
        users are in the message content.
        """
        return self._users is DEFAULT_MENTIONS or self._users

    @users.setter
    def users(self, value: bool | list[Snowflake]) -> None:
        self._users = value

    @property
    def roles(self) -> bool | list[Snowflake]:
        """Controls the roles being mentioned. If ``True`` (the default) then
        roles are mentioned based on the message content. If ``False`` then
        roles are not mentioned at all. If a list of :class:`abc.Snowflake`
        is given then only the roles provided will be mentioned, provided those
        roles are in the message content.
        """
        return self._roles is DEFAULT_MENTIONS or self._roles

    @roles.setter
    def roles(self, value: bool | list[Snowflake]) -> None:
        self._roles = value

    @property
    def replied_user(self) -> bool:
        """Whether to mention the author of the message being replied to. Defaults
        to ``True``.

        .. versionadded:: 1.6
        """
        return self._replied_user is DEFAULT_MENTIONS or self._replied_user

    @replied_user.setter
    def replied_user(self, value: bool) -> None:
        self._replied_user = value

    @classmethod
    def all(cls: type[A]) -> A:
        """A factory method that returns a :class:`AllowedMentions` with all fields explicitly set to ``True``

        .. versionadded:: 1.5
        """
        return cls(everyone=True, users=True, roles=True, replied_user=True)

    @classmethod
    def none(cls: type[A]) -> A:
        """A factory method that returns a :class:`AllowedMentions` with all fields set to ``False``

        .. versionadded:: 1.5
        """
        return cls(everyone=False, users=False, roles=False, replied_user=False)

    def to_dict(self) -> AllowedMentionsPayload:
        parse: list[Literal["everyone", "users", "roles"]] = []
        data: AllowedMentionsPayload = {}  # type: ignore

        if self.everyone:
            parse.append("everyone")

        if self.users is True:
            parse.append("users")
        elif self.users is not False:
            data["users"] = [x.id for x in self.users]

        if self.roles is True:
            parse.append("roles")
        elif self.roles is not False:
            data["roles"] = [x.id for x in self.roles]

        if self.replied_user:
            data["replied_user"] = True

        data["parse"] = parse
        return data

    def merge(self, other: AllowedMentions) -> AllowedMentions:
        # Creates a new AllowedMentions by merging from another one.
        # Merge is done by using the 'self' values unless explicitly
        # overridden by the 'other' values.
        return AllowedMentions(
            everyone=_override_unless_unset(self._everyone, other._everyone),
            users=_override_unless_unset(self._users, other._users),
            roles=_override_unless_unset(self._roles, other._roles),
            replied_user=_override_unless_unset(
                self._replied_user, other._replied_user
            ),
        )

    @override
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(everyone={self.everyone}, "
            f"users={self.users}, roles={self.roles}, replied_user={self.replied_user})"
        )
