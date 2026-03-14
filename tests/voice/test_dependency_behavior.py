import logging

import pytest

import discord
from discord.voice.utils import dependencies as voice_dependencies


def test_client_warns_once_when_voice_dependencies_are_missing(caplog):
    if not voice_dependencies.get_missing_voice_dependencies():
        pytest.skip("requires an environment without the voice extra")

    voice_dependencies.VOICE_DEPENDENCY_WARNING_EMITTED = False

    with caplog.at_level(logging.WARNING, logger="discord.client"):
        discord.Client()
        discord.Client()

    warnings = [
        record.getMessage()
        for record in caplog.records
        if record.name == "discord.client"
    ]
    assert len(warnings) == 1
    assert warnings[0].endswith("voice will NOT be supported")
    for dependency in voice_dependencies.get_missing_voice_dependencies():
        assert dependency in warnings[0]


def test_voice_modules_remain_importable_without_voice_dependencies():
    if not voice_dependencies.get_missing_voice_dependencies():
        pytest.skip("requires an environment without the voice extra")

    __import__("discord")
    __import__("discord.voice")
    __import__("discord.voice.gateway")
    __import__("discord.voice.receive.reader")
