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

import discord.player as player_module


class DummySource(player_module.AudioSource):
    def read(self) -> bytes:
        return b""

    def is_opus(self) -> bool:
        return True


class DummyClient:
    def __init__(self) -> None:
        self.ws = None
        self.client = self
        self.loop = None


def test_audio_player_resume_preserves_played_frames():
    player = player_module.AudioPlayer(DummySource(), DummyClient())
    player.loops = 25
    player._played_frames_offset = 50

    player.resume(update_speaking=False)

    assert player._played_frames_offset == 75
    assert player.loops == 0
    assert player.played_frames() == 75
