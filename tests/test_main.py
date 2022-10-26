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
import pytest

from discord import Route
from discord.ext.testing import get_mock_response

from .core import client


@pytest.mark.parametrize(
    "with_counts",
    (True, False),
)
async def test_fetch_guild(client, with_counts):
    data = get_mock_response("get_guild")
    with client.patch("get_guild"):
        guild = await client.fetch_guild(881207955029110855, with_counts=with_counts)
    guild_dict = dict(
        id=str(guild.id),
        name=guild.name,
        icon=guild.icon.key if guild.icon else None,
        description=guild.description,
        splash=guild.splash.key if guild.splash else None,
        discovery_splash=guild.discovery_splash.key if guild.discovery_splash else None,
        features=guild.features,
        approximate_member_count=guild.approximate_member_count,
        approximate_presence_count=guild.approximate_presence_count,
        emojis=[
            dict(
                name=emoji.name,
                roles=emoji.roles,
                id=str(emoji.id),
                require_colons=emoji.require_colons,
                managed=emoji.managed,
                animated=emoji.animated,
                available=emoji.available,
            )
            for emoji in guild.emojis
        ],
        stickers=[
            dict(
                id=str(sticker.id),
                name=sticker.name,
                tags=sticker.emoji,
                type=sticker.type.value,
                format_type=sticker.format.value,
                description=sticker.description,
                asset="",  # Deprecated
                available=sticker.available,
                guild_id=str(sticker.guild_id),
            )
            for sticker in guild.stickers
        ],
        banner=guild.banner.key if guild.banner else None,
        owner_id=str(guild.owner_id),
        application_id=data["application_id"],  # TODO: Fix
        region=data["region"],  # Deprecated
        afk_channel_id=str(guild.afk_channel.id) if guild.afk_channel else None,
        afk_timeout=guild.afk_timeout,
        system_channel_id=str(guild._system_channel_id)
        if guild._system_channel_id
        else None,
        widget_enabled=data["widget_enabled"],  # TODO: Fix
        widget_channel_id=data["widget_channel_id"],  # TODO: Fix
        verification_level=guild.verification_level.value,
        roles=[
            dict(
                id=str(role.id),
                name=role.name,
                permissions=str(role.permissions.value),
                position=role.position,
                color=role.color.value,
                hoist=role.hoist,
                managed=role.managed,
                mentionable=role.mentionable,
                icon=role.icon.key if role.icon else None,
                unicode_emoji=role.unicode_emoji,
                flags=list(filter(lambda d: d["id"] == str(role.id), data["roles"]))[0][
                    "flags"
                ],  # TODO: Fix
            )
            for role in guild.roles
        ],
        default_message_notifications=guild.default_notifications.value,
        mfa_level=guild.mfa_level,
        explicit_content_filter=guild.explicit_content_filter.value,
        max_presences=guild.max_presences,
        max_members=guild.max_members,
        max_stage_video_channel_users=data[
            "max_stage_video_channel_users"
        ],  # TODO: Fix
        max_video_channel_users=guild.max_video_channel_users,
        vanity_url_code=data["vanity_url_code"],  # TODO: Fix
        premium_tier=guild.premium_tier,
        premium_subscription_count=guild.premium_subscription_count,
        system_channel_flags=guild.system_channel_flags.value,
        preferred_locale=guild.preferred_locale,
        rules_channel_id=str(guild._rules_channel_id)
        if guild._rules_channel_id
        else None,
        public_updates_channel_id=str(guild._public_updates_channel_id)
        if guild._public_updates_channel_id
        else None,
        hub_type=data["hub_type"],  # TODO: Fix
        premium_progress_bar_enabled=guild.premium_progress_bar_enabled,
        nsfw=data["nsfw"],  # TODO: Fix
        nsfw_level=guild.nsfw_level.value,
    )
    assert guild_dict == data
