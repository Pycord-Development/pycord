import logging

import pytest

import discord
from discord.voice.utils import dependencies as voice_dependencies


def test_client_does_not_warn_when_voice_dependencies_are_available(caplog):
    if voice_dependencies.get_missing_voice_dependencies():
        pytest.skip("requires an environment with the voice extra")

    voice_dependencies.VOICE_DEPENDENCY_WARNING_EMITTED = False

    with caplog.at_level(logging.WARNING, logger="discord.client"):
        discord.Client()

    warnings = [
        record.getMessage()
        for record in caplog.records
        if record.name == "discord.client"
    ]
    assert warnings == []


def test_voice_modules_import_with_voice_extra():
    if voice_dependencies.get_missing_voice_dependencies():
        pytest.skip("requires an environment with the voice extra")

    __import__("discord.voice")
    __import__("discord.voice.gateway")
    __import__("discord.voice.receive.reader")
