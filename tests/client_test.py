import asyncio
import os

import pytest

os.sys.path.append("..")
import discord  # noqa: E402


def test_client_attributes():
    client = discord.client.Client()
    assert client.ws is None
    assert isinstance(client.loop, asyncio.AbstractEventLoop)
    assert client.shard_id is None
    assert client.shard_count is None
    assert isinstance(client.http, discord.http.HTTPClient)


def test_client_properties():
    client = discord.client.Client()
    assert isinstance(client.latency, float)
    assert pytest.approx(client.latency, float("nan"), nan_ok=True)
    assert client.user is None
    assert client.guilds == []
    assert client.emojis == []
    assert client.stickers == []
    assert isinstance(client.cached_messages, discord.utils.SequenceProxy)
    assert client.private_channels == []
    assert client.voice_clients == []
    assert client.application_id is None
    # assert isinstance(client.application_flags, discord.flags.ApplicationFlags)
    # Issue #102 -- The previous line raises:
    # AttributeError: 'ConnectionState' object has no attribute 'application_flags'
    # import discord ; discord.client.Client().application_flags


@pytest.mark.asyncio
@pytest.mark.parametrize("token", [None, 0, 1_234_567, 1.1, 0xbadc0de, [], {}])
async def test_client_login_token_invalid_datatype(token):
    """Client login token must be a str."""
    client = discord.client.Client()
    with pytest.raises(TypeError):
        await client.login(token)
