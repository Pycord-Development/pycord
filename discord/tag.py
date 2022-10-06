from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Tuple, Union

from . import utils
from .utils import MISSING, SnowflakeList, snowflake_time
# from . import Emoji , PartialEmoji

__all__ = ("Tag",)

if TYPE_CHECKING:
    from datetime import datetime

    from .abc import Snowflake
    from .guild import Guild
    from .role import Role
    from .state import ConnectionState
    from .types.emoji import Emoji as EmojiPayload


class Tag():

    """
        An object that represents a tag that is able to be applied to a thread in a FORUM channel.
        id:	snowflake	the id of the tag
        name:	string	the name of the tag (0-20 characters)
        moderated:	boolean	whether this tag can only be added to or removed from threads by a member with the MANAGE_THREADS permission
        emoji_id:	snowflake	the id of a guild's custom emoji *
        emoji_name:	string	the unicode character of the emoji *
    """
    
    __slots__ = (
        "id",
        "name",
        "moderated",
        "emoji_id",
        "emoji_name",
        "_state",
    )

    def __init__(self, *, data: dict, state: ConnectionState):
        self._state = state
        self._update(data)

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name!r}>"

    def _update(self, data: dict):
        self.id = int(data["id"])
        self.name = data["name"]
        self.moderated = data["moderated"]
        self.emoji_id = int(data["emoji_id"]) if data["emoji_id"] else None
        self.emoji_name = data["emoji_name"]

    @classmethod
    def from_data(cls, *, data: dict, state: ConnectionState):
        return cls(data=data, state=state)

    @property
    def created_at(self) -> datetime:
        """:class:`datetime.datetime`: Returns the tag's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def emoji(self) -> Optional[Union[Emoji, PartialEmoji]]:
        """:class:`Emoji`: Returns the emoji associated with this tag."""
        from .emoji import Emoji, PartialEmoji
        if self.emoji_id is None:
            return None

        return self._state.get_emoji(self.emoji_id) or PartialEmoji(name=self.emoji_name, id=self.emoji_id)

    @property
    def guild(self) -> Optional[Guild]:
        """:class:`Guild`: Returns the guild associated with this tag."""
        return self._state._get_guild(self.guild_id)

    @property
    def guild_id(self) -> Optional[int]:
        """:class:`int`: Returns the guild ID associated with this tag."""
        return self._state.guild_id

    # @property
    # def mention(self) -> str:
    #     """:class:`str`: Returns a string that allows you to mention the tag."""
    #     return f"<#{self.id}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Tag):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "moderated": self.moderated,
            "emoji_id": self.emoji_id,
            "emoji_name": self.emoji_name,
        }
        
    
    


    def __dict__(self) -> dict:
        return self.to_dict()    
    

