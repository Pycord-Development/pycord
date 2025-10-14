from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .guild import Guild
    from .types.guild import IncidentsData as IncidentsDataPayload

__all__ = ("IncidentsData",)


class IncidentsData:
    """Represents the incidents data object for a guild.

    Attributes
    ----------
    invites_disabled_until: Optional[datetime.datetime]
        When invites will be enabled again as a :class:`datetime.datetime`, or ``None``.
    dms_disabled_until: Optional[datetime.datetime]
        When direct messages will be enabled again as a :class:`datetime.datetime`, or ``None``.
    dm_spam_detected_at: Optional[datetime.datetime]
        When DM spam was detected, or ``None``.
    raid_detected_at: Optional[datetime.datetime]
        When a raid was detected, or ``None``.
    """

    __slots__ = (
        "guild",
        "invites_disabled_until",
        "dms_disabled_until",
        "dm_spam_detected_at",
        "raid_detected_at",
    )

    def __init__(self, data: IncidentsDataPayload, guild: Optional[Guild] = None):
        self.guild = guild

        self.invites_disabled_until: datetime.datetime | None = (
            datetime.datetime.fromisoformat(s)
            if (s := data.get("invites_disabled_until"))
            else None
        )

        self.dms_disabled_until: datetime.datetime | None = (
            datetime.datetime.fromisoformat(s)
            if (s := data.get("dms_disabled_until"))
            else None
        )

        self.dm_spam_detected_at: datetime.datetime | None = (
            datetime.datetime.fromisoformat(s)
            if (s := data.get("dm_spam_detected_at"))
            else None
        )

        self.raid_detected_at: datetime.datetime | None = (
            datetime.datetime.fromisoformat(s)
            if (s := data.get("raid_detected_at"))
            else None
        )

    def to_dict(self) -> IncidentsDataPayload:
        """Converts this object back to a raw payload suitable for API use."""
        return {
            "invites_disabled_until": self.invites_disabled_until
            and self.invites_disabled_until.isoformat(),
            "dms_disabled_until": self.dms_disabled_until
            and self.dms_disabled_until.isoformat(),
            "dm_spam_detected_at": self.dm_spam_detected_at
            and self.dm_spam_detected_at.isoformat(),
            "raid_detected_at": self.raid_detected_at
            and self.raid_detected_at.isoformat(),
        }
