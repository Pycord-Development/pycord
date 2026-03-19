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


def test_voice_modules_imports_without_voice_dependencies():
    if not voice_dependencies.get_missing_voice_dependencies():
        pytest.skip("requires an environment without the voice extra")

    __import__("discord")

    with pytes.raises(MissingVoiceDependencies):
        __import__("discord.voice")

    with pytes.raises(MissingVoiceDependencies):
        __import__("discord.voice.gateway")

    with pytes.raises(MissingVoiceDependencies):
        __import__("discord.voice.receive.reader")
