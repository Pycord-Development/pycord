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
