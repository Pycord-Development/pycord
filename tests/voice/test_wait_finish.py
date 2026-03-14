import asyncio

import discord.voice.client as voice_client_module
from discord.player import AudioSource
from discord.utils import MISSING


class DummySource(AudioSource):
    def read(self) -> bytes:
        return b""

    def is_opus(self) -> bool:
        return True


class CapturingPlayer:
    def __init__(self, source, client, *, after=None) -> None:
        self.source = source
        self.client = client
        self.after = after

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


def _make_voice_client(loop: asyncio.AbstractEventLoop):
    vc = voice_client_module.VoiceClient.__new__(voice_client_module.VoiceClient)
    vc.loop = loop
    vc._player = None
    vc._player_future = None
    vc._reader = MISSING
    vc.encoder = object()
    vc.is_connected = lambda: True
    vc.is_playing = lambda: False
    return vc


def test_wait_finish_unblocks_when_stopped_and_after_called(monkeypatch):
    created_players = []

    class LocalPlayer(CapturingPlayer):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            created_players.append(self)

    monkeypatch.setattr(voice_client_module, "AudioPlayer", LocalPlayer)

    loop = asyncio.new_event_loop()
    try:
        vc = _make_voice_client(loop)
        future = vc.play(DummySource(), wait_finish=True)

        vc.stop()
        created_players[0].after(None)
        loop.run_until_complete(asyncio.sleep(0))

        assert future.done()
        assert future.result() is None
    finally:
        loop.close()


def test_wait_finish_keeps_first_result_when_stop_races(monkeypatch):
    created_players = []

    class LocalPlayer(CapturingPlayer):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            created_players.append(self)

    monkeypatch.setattr(voice_client_module, "AudioPlayer", LocalPlayer)

    loop = asyncio.new_event_loop()
    try:
        vc = _make_voice_client(loop)
        future = vc.play(DummySource(), wait_finish=True)

        err = RuntimeError("boom")
        created_players[0].after(err)
        vc.stop()
        loop.run_until_complete(asyncio.sleep(0))

        assert future.done()
        assert future.result() is err
    finally:
        loop.close()
