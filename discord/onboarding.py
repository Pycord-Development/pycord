"""
The MIT License (MIT)

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

from random import randint
from typing import TYPE_CHECKING, Any

from .enums import OnboardingMode, PromptType, try_enum
from .partial_emoji import PartialEmoji
from .utils import MISSING, _get_as_snowflake, cached_property, get

if TYPE_CHECKING:
    from .abc import Snowflake
    from .channel import ForumChannel, TextChannel, VoiceChannel
    from .emoji import Emoji
    from .guild import Guild
    from .object import Object
    from .partial_emoji import PartialEmoji
    from .types.onboarding import Onboarding as OnboardingPayload
    from .types.onboarding import OnboardingPrompt as OnboardingPromptPayload
    from .types.onboarding import PromptOption as PromptOptionPayload

__all__ = (
    "Onboarding",
    "OnboardingPrompt",
    "PromptOption",
    "PromptType",
)


class PromptOption:
    """Represents an onboarding prompt option displayed in :class:`OnboardingPrompt`

    .. versionadded:: 2.5

    Attributes
    ----------

    id: :class:`int`
        The id of the prompt option.
    channels: List[:class:`Snowflake`]
        The channels assigned to the user when they select this option.
    roles: List[:class:`Snowflake`]
        The roles assigned to the user when they select this option.
    emoji: Union[:class:`Emoji`, :class:`PartialEmoji`]
        The emoji displayed with the option.
    title: :class`str`
        The option's title.
    description: Optional[:class:`str`]
        The option's description.
    """

    def __init__(
        self,
        title: str,
        channels: list[Snowflake] | None = None,
        roles: list[Snowflake] | None = None,
        description: str | None = None,
        emoji: Emoji | PartialEmoji | None = None,
        id: int | None = None,
    ):
        # ID is required when making edits, but it can be any snowflake that isn't already used by another prompt during edits
        self.id: int | None = id or randint(10000000000000000)
        self.title: str = title
        self.channels: list[Snowflake] = channels or []
        self.roles: list[Snowflake] = roles or []
        self.description: str | None = description
        self.emoji: Emoji | PartialEmoji | None = emoji

    def __repr__(self):
        return f"<PromptOption id={self.id} title={self.title}) channels={self.channels} roles={self.roles}>"

    def to_dict(self) -> PromptOptionPayload:
        dict_: PromptOptionPayload = {
            "title": self.title,
            "description": self.description,
            "channel_ids": [channel.id for channel in self.channels],
            "role_ids": [role.id for role in self.roles],
            "emoji": None,
            "id": str(self.id),
        }
        if self.emoji:
            dict_["emoji"] = self.emoji.to_dict()

        return dict_

    @classmethod
    def _from_dict(cls, data: PromptOptionPayload, guild: Guild) -> PromptOption:
        channel_ids = [int(channel_id) for channel_id in data.get("channel_ids", [])]
        channels = [guild.get_channel(channel_id) for channel_id in channel_ids]
        role_ids = [int(role_id) for role_id in data.get("role_ids", [])]
        roles = [guild.get_role(role_id) for role_id in role_ids]
        title = data.get("title")
        description = data.get("description")
        emoji = data.get("emoji")
        if emoji:
            if emoji.get(
                "name"
            ):  # You can currently get emoji as {'id': None, 'name': None, 'animated': False} ...
                emoji = PartialEmoji.from_dict(emoji)
            else:
                emoji = None
        return cls(channels=channels, roles=roles, title=title, description=description, emoji=emoji, id=id)  # type: ignore


class OnboardingPrompt:
    """Represents an onboarding prompt displayed in :class:`Onboarding`

    .. versionadded:: 2.5

    Attributes
    ----------

    id: :class:`int`
        The id of the prompt.
    type: :class:`PromptType`
        The type of onboarding prompt.
    options: List[:class:`PromptOption`]
        The list of options available in the prompt.
    title: :class:`str`
        The prompt's title.
    single_select: :class:`bool`
        Whether the user is limited to selecting one option on this prompt.
    required: :class:`bool`
        Whether the user is required to answer this prompt.
    in_onboarding: :class:`bool`
        Whether this prompt is displayed in the initial onboarding flow.
    """

    def __init__(
        self,
        type: PromptType,
        title: str,
        options: list[PromptOption],
        single_select: bool,
        required: bool,
        in_onboarding: bool,
        id: int | None = None,  # Currently optional as users can manually create these
    ):
        # ID is required when making edits, but it can be any snowflake that isn't already used by another prompt during edits
        self.id: int | None = id or randint(10000000000000000)
        self.type: PromptType = type
        if isinstance(self.type, int):
            self.type = try_enum(PromptType, self.type)
        self.options: list[PromptOption] = options
        self.title: str = title
        self.single_select: bool = single_select
        self.required: bool = required
        self.in_onboarding: bool = in_onboarding

    def __repr__(self):
        return f"<OnboardingPrompt (title={self.title} required={self.required})>"

    def to_dict(self) -> OnboardingPromptPayload:
        dict_: OnboardingPromptPayload = {
            "type": self.type.value,
            "title": self.title,
            "single_select": self.single_select,
            "required": self.required,
            "in_onboarding": self.in_onboarding,
            "options": [option.to_dict() for option in self.options],
            "id": self.id,
        }

        return dict_

    @classmethod
    def _from_dict(
        cls, data: OnboardingPromptPayload, guild: Guild
    ) -> OnboardingPrompt:
        id = data.get("id")
        type = try_enum(PromptType, data.get("type"))
        title = data.get("title")
        single_select = data.get("single_select")
        required = data.get("required")
        in_onboarding = data.get("in_onboarding")
        options = [
            PromptOption._from_dict(option, guild) for option in data.get("options", [])
        ]

        return cls(type=type, title=title, single_select=single_select, required=required, in_onboarding=in_onboarding, options=options, id=id)  # type: ignore


class Onboarding:
    """Represents the Onboarding flow for a guild.

    .. versionadded:: 2.5

    Attributes
    ----------

    prompts: List[:class:`OnboardingPrompt`]
        A list of prompts displayed in the onboarding flow.
    enabled: :class:`bool`
        Whether onboarding is enabled in the guild.
    mode: :class:`OnboardingMode`
        The current onboarding mode.
    """

    def __init__(self, data: OnboardingPayload, guild: Guild):
        self._guild = guild
        self._update(data)

    def __repr__(self):
        return f"<Onboarding enabled={self.enabled} default_channels={self.default_channels_channels}>"

    def _update(self, data: OnboardingPayload):
        self.guild_id: Snowflake = data["guild_id"]
        self.prompts: list[OnboardingPrompt] = [
            OnboardingPrompt._from_dict(prompt, self._guild)
            for prompt in data.get("prompts", [])
        ]
        self.default_channel_ids: list[int] = [
            int(c) for c in data["default_channel_ids"]
        ]
        self.enabled: bool = data["enabled"]
        self.mode: OnboardingMode = try_enum(OnboardingMode, data.get("mode"))

    @property
    def guild(self) -> Guild:
        """The guild this onboarding flow belongs to."""
        return self._guild

    @cached_property
    def default_channels(
        self,
    ) -> list[TextChannel | ForumChannel | VoiceChannel | Object]:
        """The channels that members are opted into by default.

        If a channel is not found in the guild's cache,
        then it will be returned as an :class:`Object`.
        """
        if self.guild is None:
            return [Object(channel_id) for channel_id in self.default_channel_ids]
        return [
            self.guild.get_channel(channel_id) or Object(channel_id)
            for channel_id in self.default_channel_ids
        ]

    async def edit(
        self,
        *,
        prompts: list[OnboardingPrompt] | None = MISSING,
        default_channels: list[Snowflake] | None = MISSING,
        enabled: bool | None = MISSING,
        mode: OnboardingMode | None = MISSING,
        reason: str | None = MISSING,
    ) -> Onboarding:
        """|coro|

        Edits this onboarding flow.

        You must have the :attr:`~Permissions.manage_guild` and :attr:`~Permissions.manage_roles` permissions in the
        guild to do this.

        Parameters
        ----------

        prompts: Optional[List[:class:`OnboardingPrompt`]]
            The new list of prompts for this flow.
        default_channels: Optional[List[:class:`Snowflake`]]
            The new default channels that users are opted into.
        enabled: Optional[:class:`bool`]
            Whether onboarding should be enabled. Setting this to True requires the guild to have ``COMMUNITY`` in :attr:`~Guild.features`
            and at least 7 ``default_channels``.
        mode: Optional[:class:`OnboardingMode`]
            The new onboarding mode.
        reason: Optional[:class:`str`]
            The reason that shows up on Audit log.

        Raises
        ------

        HTTPException
            Editing the onboarding flow failed somehow.
        Forbidden
            You don't have permissions to edit the onboarding flow.
        NotFound
            This onboarding flow does not exist.
        """

        fields: dict[str, Any] = {}
        if prompts is not MISSING:
            fields["prompts"] = [prompt.to_dict() for prompt in prompts]

        if default_channels is not MISSING:
            fields["default_channel_ids"] = [channel.id for channel in default_channels]

        if enabled is not MISSING:
            fields["enabled"] = enabled

        if mode is not MISSING:
            fields["mode"] = mode.value

        new = await self._guild._state.http.edit_onboarding(
            self._guild.id, fields, reason=reason
        )
        self._update(new)

        return self
