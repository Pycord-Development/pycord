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

from pathlib import Path
from random import choice, randint, randrange, sample
from typing import Literal, get_args

import pytest

from discord import File, Route
from discord.ext.testing.fixtures import (
    after,
    before,
    channel_id,
    guild_id,
    icon,
    limit,
    name,
    reason,
    user_id,
)
from discord.ext.testing.helpers import (
    random_amount,
    random_bool,
    random_bytes,
    random_snowflake,
    random_string,
)
from discord.types.guild import GuildFeature

from ..core import client


@pytest.fixture()
def code():
    return random_string(10)


@pytest.fixture()
def description():
    return random_string(100)


async def test_get_guilds(client, limit, before, after):
    params = {"limit": limit}
    if before:
        params["before"] = before
    if after:
        params["after"] = after
    with client.makes_request(Route("GET", "/users/@me/guilds"), params=params):
        await client.http.get_guilds(limit, before, after)


async def test_leave_guild(client, guild_id):
    with client.makes_request(
        Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id)
    ):
        await client.http.leave_guild(guild_id)


@pytest.mark.parametrize(
    "with_counts",
    (True, False),
)
async def test_get_guild(client, guild_id, with_counts):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}", guild_id=guild_id),
        params={"with_counts": int(with_counts)},
    ):
        await client.http.get_guild(guild_id, with_counts=with_counts)


async def test_delete_guild(client, guild_id):
    with client.makes_request(Route("DELETE", "/guilds/{guild_id}", guild_id=guild_id)):
        await client.http.delete_guild(guild_id)


async def test_create_guild(client, name, icon):
    payload = {"name": name}
    if icon:
        payload["icon"] = icon
    with client.makes_request(Route("POST", "/guilds"), json=payload):
        await client.http.create_guild(name, icon)


@pytest.mark.parametrize(
    "channel_id1,channel_id2, channel_id3",
    ((random_snowflake(), random_snowflake(), random_snowflake()),),
)
@pytest.mark.parametrize("premium_progress_bar_enabled", (True, False))
@pytest.mark.parametrize("verification_level", (randint(0, 4),))
@pytest.mark.parametrize("default_message_notifications", (randint(0, 1),))
@pytest.mark.parametrize("explicit_content_filter", (randint(0, 2),))
@pytest.mark.parametrize("splash", (random_bytes(),))
@pytest.mark.parametrize("discovery_splash", (random_bytes(),))
@pytest.mark.parametrize("banner", (random_bytes(),))
@pytest.mark.parametrize("system_channel_flags", (randint(0, 1 << 4),))
@pytest.mark.parametrize("preferred_locale", (random_string(5),))
@pytest.mark.parametrize(
    "features",
    (sample(get_args(GuildFeature), randint(0, len(get_args(GuildFeature)))),),
)
@pytest.mark.parametrize("afk_timeout", (choice((60, 300, 900, 1800, 3600)),))
async def test_edit_guild(
    client,
    name,
    verification_level,
    default_message_notifications,
    explicit_content_filter,
    channel_id3,
    afk_timeout,
    icon,
    user_id,
    splash,
    discovery_splash,
    banner,
    channel_id,
    system_channel_flags,
    channel_id1,
    channel_id2,
    preferred_locale,
    features,
    description,
    premium_progress_bar_enabled,
    reason,
):
    payload = {
        "name": name,
        "verification_level": verification_level,
        "default_message_notifications": default_message_notifications,
        "explicit_content_filter": explicit_content_filter,
        "afk_channel_id": channel_id3,
        "afk_timeout": afk_timeout,
        "icon": icon,
        "owner_id": user_id,
        "splash": splash,
        "discovery_splash": discovery_splash,
        "banner": banner,
        "system_channel_id": channel_id,
        "system_channel_flags": system_channel_flags,
        "rules_channel_id": channel_id1,
        "public_updates_channel_id": channel_id2,
        "preferred_locale": preferred_locale,
        "features": features,
        "description": description,
        "premium_progress_bar_enabled": premium_progress_bar_enabled,
    }
    with client.makes_request(
        Route("PATCH", "/guilds/{guild_id}", guild_id=guild_id),
        json=payload,
        reason=reason,
    ):
        await client.http.edit_guild(
            guild_id,
            reason=reason,
            **payload,
        )


@pytest.mark.parametrize("required", [random_bool()])
async def test_edit_guild_mfa(client, guild_id, required, reason):
    payload = {"level": int(required)}
    with client.makes_request(
        Route("POST", "/guilds/{guild_id}/mfa", guild_id=guild_id),
        json=payload,
        reason=reason,
    ):
        await client.http.edit_guild_mfa(
            guild_id,
            required,
            reason=reason,
        )


async def test_get_template(client, code):
    with client.makes_request(Route("GET", "/guilds/templates/{code}", code=code)):
        await client.http.get_template(code)


async def test_guild_templates(client, guild_id):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/templates", guild_id=guild_id)
    ):
        await client.http.guild_templates(guild_id)


async def test_create_template(client, guild_id, name, icon):
    payload = {"name": name, "icon": icon}
    with client.makes_request(
        Route("POST", "/guilds/{guild_id}/templates", guild_id=guild_id),
        json=payload,
    ):
        await client.http.create_template(guild_id, payload)


async def test_sync_template(client, guild_id, code):
    with client.makes_request(
        Route(
            "PUT", "/guilds/{guild_id}/templates/{code}", guild_id=guild_id, code=code
        )
    ):
        await client.http.sync_template(guild_id, code)


async def test_edit_template(client, guild_id, code, name, description):
    payload = {"name": name, "description": description}
    with client.makes_request(
        Route(
            "PATCH", "/guilds/{guild_id}/templates/{code}", guild_id=guild_id, code=code
        ),
        json=payload,
    ):
        await client.http.edit_template(guild_id, code, payload)


async def test_delete_template(client, guild_id, code):
    with client.makes_request(
        Route(
            "DELETE",
            "/guilds/{guild_id}/templates/{code}",
            guild_id=guild_id,
            code=code,
        )
    ):
        await client.http.delete_template(guild_id, code)


async def test_create_from_template(client, code, name, icon):
    payload = {"name": name}
    if icon is not None:
        payload["icon"] = icon
    with client.makes_request(
        Route("POST", "/guilds/templates/{code}", code=code), json=payload
    ):
        await client.http.create_from_template(code, name, icon)


# limit is optional on this route
@pytest.mark.parametrize("limit", [None, randrange(0, 1000)])
async def test_get_bans(client, guild_id, limit, before, after):
    params = {}
    if limit is not None:
        params["limit"] = limit
    if before is not None:
        params["before"] = before
    if after is not None:
        params["after"] = after
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/bans", guild_id=guild_id), params=params
    ):
        await client.http.get_bans(guild_id, limit=limit, before=before, after=after)


async def test_get_ban(client, guild_id, user_id):
    with client.makes_request(
        Route(
            "GET",
            "/guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
    ):
        await client.http.get_ban(user_id, guild_id)


async def test_get_vanity_code(client, guild_id):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id)
    ):
        await client.http.get_vanity_code(guild_id)


async def test_change_vanity_code(client, guild_id, code, reason):
    with client.makes_request(
        Route("PATCH", "/guilds/{guild_id}/vanity-url", guild_id=guild_id),
        json={"code": code},
        reason=reason,
    ):
        await client.http.change_vanity_code(guild_id, code, reason=reason)


async def test_get_all_guild_channels(client, guild_id):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id)
    ):
        await client.http.get_all_guild_channels(guild_id)


async def test_get_members(client, guild_id, limit, after):
    payload = {"limit": limit}
    if after is not None:
        payload["after"] = after
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/members", guild_id=guild_id), params=payload
    ):
        await client.http.get_members(guild_id, limit=limit, after=after)


async def test_get_member(client, guild_id, user_id):
    with client.makes_request(
        Route(
            "GET",
            "/guilds/{guild_id}/members/{member_id}",
            guild_id=guild_id,
            member_id=user_id,
        )
    ):
        await client.http.get_member(guild_id, user_id)


@pytest.fixture(params=[0, randint(1, 10)])
def roles(request) -> list[str]:
    return [str(random_snowflake()) for _ in range(request.param)]


@pytest.fixture()
def days() -> int:
    return randint(1, 30)


@pytest.mark.parametrize("compute_prune_count", [True, False])
async def test_prune_members(
    client, guild_id, days, compute_prune_count, roles, reason
):
    payload = {
        "days": days,
        "compute_prune_count": "true" if compute_prune_count else "false",
    }
    if roles:
        payload["include_roles"] = ", ".join(roles)

    with client.makes_request(
        Route("POST", "/guilds/{guild_id}/prune", guild_id=guild_id),
        json=payload,
        reason=reason,
    ):
        await client.http.prune_members(
            guild_id, days, compute_prune_count, roles, reason=reason
        )


async def test_estimate_pruned_members(client, guild_id, days, roles):
    payload = {"days": days}
    if roles:
        payload["include_roles"] = ", ".join(roles)

    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id), params=payload
    ):
        await client.http.estimate_pruned_members(guild_id, days, roles)


@pytest.fixture()
def sticker_id() -> int:
    return random_snowflake()


async def test_get_sticker(client, sticker_id):
    with client.makes_request(
        Route("GET", "/stickers/{sticker_id}", sticker_id=sticker_id)
    ):
        await client.http.get_sticker(sticker_id)


async def test_list_premium_sticker_packs(client):
    with client.makes_request(Route("GET", "/sticker-packs")):
        await client.http.list_premium_sticker_packs()


async def test_get_all_guild_stickers(client, guild_id):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/stickers", guild_id=guild_id)
    ):
        await client.http.get_all_guild_stickers(guild_id)


async def test_get_guild_sticker(client, guild_id, sticker_id):
    with client.makes_request(
        Route(
            "GET",
            "/guilds/{guild_id}/stickers/{sticker_id}",
            guild_id=guild_id,
            sticker_id=sticker_id,
        )
    ):
        await client.http.get_guild_sticker(guild_id, sticker_id)


@pytest.fixture(
    params=(
        "png",
        "json",  # Lottie
        "txt",  # octet-stream
    )
)
def file_type(request) -> Literal["png", "json", "txt"]:
    return request.param


@pytest.fixture()
def sticker_file(file_type) -> File:
    return File(Path(__file__).parent.parent / "assets" / ("test." + file_type))


@pytest.fixture()
def tags() -> str:
    return random_string()


async def test_create_guild_sticker(
    client, guild_id, name, description, tags, sticker_file, file_type, reason
):
    if file_type == "json":
        content_type = "application/json"
    elif file_type == "txt":
        content_type = "application/octet-stream"
    else:
        content_type = f"image/{file_type}"

    form = [
        {
            "name": "file",
            "value": sticker_file.fp,
            "filename": sticker_file.filename,
            "content_type": content_type,
        }
    ]

    payload = {"name": name, "tags": tags, "description": description}

    for k, v in payload.items():
        form.append(
            {
                "name": k,
                "value": v,
            }
        )

    with client.makes_request(
        Route("POST", "/guilds/{guild_id}/stickers", guild_id=guild_id),
        form=form,
        reason=reason,
        files=[sticker_file],
    ):
        await client.http.create_guild_sticker(
            guild_id,
            payload,
            sticker_file,
            reason,
        )


async def test_modify_guild_sticker(
    client, guild_id, sticker_id, name, description, tags, reason
):
    payload = {"name": name, "tags": tags, "description": description}
    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/stickers/{sticker_id}",
            guild_id=guild_id,
            sticker_id=sticker_id,
        ),
        json=payload,
        reason=reason,
    ):
        await client.http.modify_guild_sticker(
            guild_id,
            sticker_id,
            payload,
            reason,
        )


async def test_delete_guild_sticker(client, guild_id, sticker_id, reason):
    with client.makes_request(
        Route(
            "DELETE",
            "/guilds/{guild_id}/stickers/{sticker_id}",
            guild_id=guild_id,
            sticker_id=sticker_id,
        ),
        reason=reason,
    ):
        await client.http.delete_guild_sticker(
            guild_id,
            sticker_id,
            reason,
        )


async def test_get_all_custom_emojis(client, guild_id):
    with client.makes_request(
        Route("GET", "/guilds/{guild_id}/emojis", guild_id=guild_id)
    ):
        await client.http.get_all_custom_emojis(guild_id)


@pytest.fixture()
async def emoji_id() -> int:
    return random_snowflake()


async def test_get_custom_emoji(client, guild_id, emoji_id):
    with client.makes_request(
        Route(
            "GET",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        )
    ):
        await client.http.get_custom_emoji(guild_id, emoji_id)


@pytest.mark.parametrize("roles", (random_amount(random_snowflake), None))
@pytest.mark.parametrize("image", [random_bytes()])
async def test_create_custom_emoji(client, guild_id, name, image, roles, reason):
    payload = {
        "name": name,
        "image": image,
        "roles": roles or [],
    }

    with client.makes_request(
        Route("POST", "/guilds/{guild_id}/emojis", guild_id=guild_id),
        json=payload,
        reason=reason,
    ):
        await client.http.create_custom_emoji(
            guild_id,
            name,
            image,
            roles=roles,
            reason=reason,
        )


async def test_delete_custom_emoji(client, guild_id, emoji_id, reason):
    with client.makes_request(
        Route(
            "DELETE",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        ),
        reason=reason,
    ):
        await client.http.delete_custom_emoji(
            guild_id,
            emoji_id,
            reason=reason,
        )


@pytest.mark.parametrize("roles", (random_amount(random_snowflake), None))
async def test_edit_custom_emoji(client, guild_id, emoji_id, name, roles, reason):
    payload = {
        "name": name,
        "roles": roles,
    }

    with client.makes_request(
        Route(
            "PATCH",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        ),
        json=payload,
        reason=reason,
    ):
        await client.http.edit_custom_emoji(
            guild_id,
            emoji_id,
            payload=payload,
            reason=reason,
        )
