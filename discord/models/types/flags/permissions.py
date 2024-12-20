from __future__ import annotations

from collections.abc import Callable
from typing import Any

from typing_extensions import Self, final

from .base import BaseFlags, alias_flag_value, flag_value


class permission_alias(alias_flag_value):
    alias: str  # pyright: ignore [reportUninitializedInstanceVariable]


def make_permission_alias(
    alias: str,
) -> Callable[
    [Callable[[Any], int]], permission_alias
]:  # pyright: ignore [reportExplicitAny]
    def decorator(
        func: Callable[[Any], int]
    ) -> permission_alias:  # pyright: ignore [reportExplicitAny]
        ret = permission_alias(func)
        ret.alias = alias
        return ret

    return decorator


@final
class Permissions(BaseFlags):
    """Wraps up the Discord permission value.

    The properties provided are two way. You can set and retrieve individual
    bits using the properties as if they were regular bools. This allows
    you to edit permissions.

    .. versionchanged:: 1.3
        You can now use keyword arguments to initialize :class:`Permissions`
        similar to :meth:`update`.

    .. container:: operations

        .. describe:: x == y

            Checks if two permissions are equal.
        .. describe:: x != y

            Checks if two permissions are not equal.
        .. describe:: x <= y

            Checks if a permission is a subset of another permission.
        .. describe:: x >= y

            Checks if a permission is a superset of another permission.
        .. describe:: x < y

             Checks if a permission is a strict subset of another permission.
        .. describe:: x > y

        .. describe:: x + y

            Adds two permissions together. Equivalent to ``x | y``.
        .. describe:: x - y

            Subtracts two permissions from each other.
        .. describe:: x | y

            Returns the union of two permissions. Equivalent to ``x + y``.
        .. describe:: x & y

            Returns the intersection of two permissions.
        .. describe:: ~x

            Returns the inverse of a permission.

             Checks if a permission is a strict superset of another permission.
        .. describe:: hash(x)

               Return the permission's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(perm, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.
               Note that aliases are not shown.

    Attributes
    ----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available permissions. You should query
        permissions via the properties rather than using this raw value.
    """

    __slots__: tuple[str] = tuple()

    def __init__(
        self, permissions: int = 0, **kwargs: bool
    ) -> None:  # pyright: ignore [reportMissingSuperCall]
        if not isinstance(
            permissions, int
        ):  # pyright: ignore [reportUnnecessaryIsInstance]
            raise TypeError(  # pyright: ignore [reportUnreachable]
                f"Expected int parameter, received {permissions.__class__.__name__} instead."
            )

        self.value = permissions
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid permission name.")
            setattr(self, key, value)

    def is_subset(self, other: Any) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if self has the same or fewer permissions as other."""
        if isinstance(other, Permissions):
            return (self.value & other.value) == self.value
        raise TypeError(
            f"Cannot compare {self.__class__.__name__} with {other.__class__.__name__}"
        )

    def is_superset(self, other: Any) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if self has the same or more permissions as other."""
        if isinstance(other, Permissions):
            return (self.value | other.value) == self.value
        else:
            raise TypeError(
                f"cannot compare {self.__class__.__name__} with {other.__class__.__name__}"
            )

    def is_strict_subset(
        self, other: Any
    ) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if the permissions on other are a strict subset of those on self."""
        return self.is_subset(other) and self != other

    def is_strict_superset(
        self, other: Any
    ) -> bool:  # pyright: ignore [reportExplicitAny]
        """Returns ``True`` if the permissions on other are a strict superset of those on self."""
        return self.is_superset(other) and self != other

    __le__: Callable[[Self, Any], bool] = (
        is_subset  # pyright: ignore [reportExplicitAny]
    )
    __ge__: Callable[[Self, Any], bool] = (
        is_superset  # pyright: ignore [reportExplicitAny]
    )
    __lt__: Callable[[Self, Any], bool] = (
        is_strict_subset  # pyright: ignore [reportExplicitAny]
    )
    __gt__: Callable[[Self, Any], bool] = (
        is_strict_superset  # pyright: ignore [reportExplicitAny]
    )

    @classmethod
    def none(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        permissions set to ``False``.
        """
        return cls(0)

    @classmethod
    def all(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        permissions set to ``True``.
        """
        return cls(0b1111111111111111111111111111111111111111111111111)

    @classmethod
    def all_channel(cls: type[Self]) -> Self:
        """A :class:`Permissions` with all channel-specific permissions set to
        ``True`` and the guild-specific ones set to ``False``. The guild-specific
        permissions are currently:

        - :attr:`manage_emojis`
        - :attr:`view_audit_log`
        - :attr:`view_guild_insights`
        - :attr:`view_creator_monetization_analytics`
        - :attr:`manage_guild`
        - :attr:`change_nickname`
        - :attr:`manage_nicknames`
        - :attr:`kick_members`
        - :attr:`ban_members`
        - :attr:`administrator`

        .. versionchanged:: 1.7
           Added :attr:`stream`, :attr:`priority_speaker` and :attr:`use_slash_commands` permissions.

        .. versionchanged:: 2.0
           Added :attr:`create_public_threads`, :attr:`create_private_threads`, :attr:`manage_threads`,
           :attr:`use_external_stickers`, :attr:`send_messages_in_threads` and
           :attr:`request_to_speak` permissions.
        """
        return cls(0b111110110110011111101111111111101010001)

    @classmethod
    def general(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "General" permissions from the official Discord UI set to ``True``.

        .. versionchanged:: 1.7
           Permission :attr:`read_messages` is now included in the general permissions, but
           permissions :attr:`administrator`, :attr:`create_instant_invite`, :attr:`kick_members`,
           :attr:`ban_members`, :attr:`change_nickname` and :attr:`manage_nicknames` are
           no longer part of the general permissions.
        .. versionchanged:: 2.7
           Added :attr:`view_creator_monetization_analytics` permission.
        """
        return cls(0b100000000001110000000010000000010010110000)

    @classmethod
    def membership(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Membership" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7
        """
        return cls(0b00001100000000000000000000000111)

    @classmethod
    def text(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Text" permissions from the official Discord UI set to ``True``.

        .. versionchanged:: 1.7
           Permission :attr:`read_messages` is no longer part of the text permissions.
           Added :attr:`use_slash_commands` permission.

        .. versionchanged:: 2.0
           Added :attr:`create_public_threads`, :attr:`create_private_threads`, :attr:`manage_threads`,
           :attr:`send_messages_in_threads` and :attr:`use_external_stickers` permissions.
        """
        return cls(0b111110010000000000001111111100001000000)

    @classmethod
    def voice(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Voice" permissions from the official Discord UI set to ``True``.
        """
        return cls(0b1001001001000000000000011111100000000001100000000)

    @classmethod
    def stage(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Stage Channel" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7
        """
        return cls(1 << 32)

    @classmethod
    def stage_moderator(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Stage Moderator" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7
        """
        return cls(0b100000001010000000000000000000000)

    @classmethod
    def advanced(cls: type[Self]) -> Self:
        """A factory method that creates a :class:`Permissions` with all
        "Advanced" permissions from the official Discord UI set to ``True``.

        .. versionadded:: 1.7
        """
        return cls(1 << 3)

    def update(self, **kwargs: bool) -> None:
        r"""Bulk updates this permission object.

        Allows you to set multiple attributes by using keyword
        arguments. The names must be equivalent to the properties
        listed. Extraneous key/value pairs will be silently ignored.

        Parameters
        ------------
        \*\*kwargs
            A list of key/value pairs to bulk update permissions with.
        """
        for key, value in kwargs.items():
            if key in self.VALID_FLAGS:
                setattr(self, key, value)

    def handle_overwrite(self, allow: int, deny: int) -> None:
        # Basically this is what's happening here.
        # We have an original bit array, e.g. 1010
        # Then we have another bit array that is 'denied', e.g. 1111
        # And then we have the last one which is 'allowed', e.g. 0101
        # We want original OP denied to end up resulting in
        # whatever is in denied to be set to 0.
        # So 1010 OP 1111 -> 0000
        # Then we take this value and look at the allowed values.
        # And whatever is allowed is set to 1.
        # So 0000 OP2 0101 -> 0101
        # The OP is base  & ~denied.
        # The OP2 is base | allowed.
        self.value = (self.value & ~deny) | allow

    @flag_value
    def create_instant_invite(self) -> int:
        """:class:`bool`: Returns ``True`` if the user can create instant invites."""
        return 1 << 0

    @flag_value
    def kick_members(self) -> int:
        """:class:`bool`: Returns ``True`` if the user can kick users from the guild."""
        return 1 << 1

    @flag_value
    def ban_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can ban users from the guild."""
        return 1 << 2

    @flag_value
    def administrator(self) -> int:
        """:class:`bool`: Returns ``True`` if a user is an administrator. This role overrides all other permissions.

        This also bypasses all channel-specific overrides.
        """
        return 1 << 3

    @flag_value
    def manage_channels(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can edit, delete, or create channels in the guild.

        This also corresponds to the "Manage Channel" channel-specific override.
        """
        return 1 << 4

    @flag_value
    def manage_guild(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can edit guild properties."""
        return 1 << 5

    @flag_value
    def add_reactions(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can add reactions to messages."""
        return 1 << 6

    @flag_value
    def view_audit_log(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can view the guild's audit log."""
        return 1 << 7

    @flag_value
    def priority_speaker(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can be more easily heard while talking."""
        return 1 << 8

    @flag_value
    def stream(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can stream in a voice channel."""
        return 1 << 9

    @flag_value
    def view_channel(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can view all or specific channels."""
        return 1 << 10

    @make_permission_alias("view_channel")
    def read_messages(self) -> int:
        """:class:`bool`: An alias for :attr:`view_channel`.

        .. versionadded:: 1.3
        """
        return 1 << 10

    @flag_value
    def send_messages(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send messages from all or specific text channels."""
        return 1 << 11

    @flag_value
    def send_tts_messages(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send TTS messages from all or specific text channels."""
        return 1 << 12

    @flag_value
    def manage_messages(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can delete or pin messages in a text channel.

        .. note::

            Note that there are currently no ways to edit other people's messages.
        """
        return 1 << 13

    @flag_value
    def embed_links(self) -> int:
        """:class:`bool`: Returns ``True`` if a user's messages will automatically be embedded by Discord."""
        return 1 << 14

    @flag_value
    def attach_files(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send files in their messages."""
        return 1 << 15

    @flag_value
    def read_message_history(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can read a text channel's previous messages."""
        return 1 << 16

    @flag_value
    def mention_everyone(self) -> int:
        """:class:`bool`: Returns ``True`` if a user's @everyone or @here will mention everyone in the text channel."""
        return 1 << 17

    @flag_value
    def external_emojis(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use emojis from other guilds."""
        return 1 << 18

    @make_permission_alias("external_emojis")
    def use_external_emojis(self) -> int:
        """:class:`bool`: An alias for :attr:`external_emojis`.

        .. versionadded:: 1.3
        """
        return 1 << 18

    @flag_value
    def view_guild_insights(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can view the guild's insights.

        .. versionadded:: 1.3
        """
        return 1 << 19

    @flag_value
    def connect(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can connect to a voice channel."""
        return 1 << 20

    @flag_value
    def speak(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can speak in a voice channel."""
        return 1 << 21

    @flag_value
    def mute_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can mute other users."""
        return 1 << 22

    @flag_value
    def deafen_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can deafen other users."""
        return 1 << 23

    @flag_value
    def move_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can move users between other voice channels."""
        return 1 << 24

    @flag_value
    def use_voice_activation(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use voice activation in voice channels."""
        return 1 << 25

    @flag_value
    def change_nickname(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can change their nickname in the guild."""
        return 1 << 26

    @flag_value
    def manage_nicknames(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can change other user's nickname in the guild."""
        return 1 << 27

    @flag_value
    def manage_roles(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create or edit roles less than their role's position.

        This also corresponds to the "Manage Permissions" channel-specific override.
        """
        return 1 << 28

    @make_permission_alias("manage_roles")
    def manage_permissions(self) -> int:
        """:class:`bool`: An alias for :attr:`manage_roles`.

        .. versionadded:: 1.3
        """
        return 1 << 28

    @flag_value
    def manage_webhooks(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create, edit, or delete webhooks."""
        return 1 << 29

    @flag_value
    def manage_emojis(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create, edit, or delete emojis."""
        return 1 << 30

    @make_permission_alias("manage_emojis")
    def manage_emojis_and_stickers(self) -> int:
        """:class:`bool`: An alias for :attr:`manage_emojis`.

        .. versionadded:: 2.0
        """
        return 1 << 30

    @flag_value
    def use_slash_commands(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use slash commands.

        .. versionadded:: 1.7
        """
        return 1 << 31

    @make_permission_alias("use_slash_commands")
    def use_application_commands(self) -> int:
        """:class:`bool`: An alias for :attr:`use_slash_commands`.

        .. versionadded:: 2.0
        """
        return 1 << 31

    @flag_value
    def request_to_speak(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can request to speak in a stage channel.

        .. versionadded:: 1.7
        """
        return 1 << 32

    @flag_value
    def manage_events(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can manage guild events.

        .. versionadded:: 2.0
        """
        return 1 << 33

    @flag_value
    def manage_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can manage threads.

        .. versionadded:: 2.0
        """
        return 1 << 34

    @flag_value
    def create_public_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create public threads.

        .. versionadded:: 2.0
        """
        return 1 << 35

    @flag_value
    def create_private_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can create private threads.

        .. versionadded:: 2.0
        """
        return 1 << 36

    @flag_value
    def external_stickers(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use stickers from other guilds.

        .. versionadded:: 2.0
        """
        return 1 << 37

    @make_permission_alias("external_stickers")
    def use_external_stickers(self) -> int:
        """:class:`bool`: An alias for :attr:`external_stickers`.

        .. versionadded:: 2.0
        """
        return 1 << 37

    @flag_value
    def send_messages_in_threads(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can send messages in threads.

        .. versionadded:: 2.0
        """
        return 1 << 38

    @flag_value
    def start_embedded_activities(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can launch an activity flagged 'EMBEDDED' in a voice channel.

        .. versionadded:: 2.0
        """
        return 1 << 39

    @flag_value
    def moderate_members(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can moderate members (timeout).

        .. versionadded:: 2.0
        """
        return 1 << 40

    @flag_value
    def view_creator_monetization_analytics(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can view creator monetization (role subscription) analytics.

        .. versionadded:: 2.7
        """
        return 1 << 41

    @flag_value
    def use_soundboard(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use the soundboard in a voice channel.

        .. versionadded:: 2.7
        """
        return 1 << 42

    @flag_value
    def use_external_sounds(self) -> int:
        """:class:`bool`: Returns ``True`` if a user can use external soundboard sounds in a voice channel.

        .. versionadded:: 2.7
        """
        return 1 << 45

    @flag_value
    def send_voice_messages(self) -> int:
        """:class:`bool`: Returns ``True`` if a member can send voice messages.

        .. versionadded:: 2.5
        """
        return 1 << 46

    @flag_value
    def set_voice_channel_status(self) -> int:
        """:class:`bool`: Returns ``True`` if a member can set voice channel status.

        .. versionadded:: 2.5
        """
        return 1 << 48

    @flag_value
    def send_polls(self) -> int:
        """:class:`bool`: Returns ``True`` if a member can send polls.

        .. versionadded:: 2.6
        """
        return 1 << 49

    @flag_value
    def use_external_apps(self) -> int:
        """:class:`bool`: Returns ``True`` if a member's user-installed apps can show public responses.
        Users will still be able to use user-installed apps, but responses will be ephemeral.

        This only applies to apps that are also not installed to the guild.

        .. versionadded:: 2.6
        """
        return 1 << 50
