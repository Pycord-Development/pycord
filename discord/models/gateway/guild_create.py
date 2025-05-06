from __future__ import annotations

from datetime import datetime

from ..base import Guild, Member
from ..types.utils import MISSING, MissingSentinel
from .base import GatewayEvent


class GuildCreateData(Guild):
    joined_at: datetime
    large: bool
    unavailable: bool | MissingSentinel = MISSING
    member_count: int
    voice_states: list[dict]  # TODO: VoiceState
    members: list[Member]
    channels: list[dict]  # TODO: Channel
    presences: list[dict]  # TODO: Presence
    stage_instances: list[dict]  # TODO: StageInstance
    guild_scheduled_events: list[dict]  # TODO: GuildScheduledEvent
    soundboard_sounds: list[dict]  # TODO: SoundboardSound


class GuildCreate(GatewayEvent[GuildCreateData]):
    pass
