import time
from types import SimpleNamespace

from discord.sinks import Sink
from discord.voice.receive import router as router_module
from discord.voice.receive.reader import SpeakingTimer


class DummySink(Sink):
    def __init__(self, *, opus=False):
        super().__init__()
        self.opus = opus
        self.writes = []
        self.vc = SimpleNamespace(guild=None)

    def is_opus(self):
        return self.opus

    def write(self, data, user):
        self.writes.append((data, user))


class DummyDecoder:
    def __init__(self, router, ssrc):
        self.router = router
        self.ssrc = ssrc
        self.pushed = []
        self.processed = []

    def push_packet(self, packet):
        self.pushed.append(packet)

    def process_packet(self, packet):
        self.processed.append(packet)
        return SimpleNamespace(source="user", packet=packet)

    def set_user_id(self, user_id):
        self.user_id = user_id

    def destroy(self):
        self.destroyed = True


class DummyPacket:
    def __init__(self, ssrc=1):
        self.ssrc = ssrc


def test_sink_is_opus_defaults_to_false():
    assert Sink().is_opus() is False


def test_packet_router_writes_pcm_packets_inline(monkeypatch):
    monkeypatch.setattr(router_module, "PacketDecoder", DummyDecoder)
    sink = DummySink(opus=False)
    packet_router = router_module.PacketRouter(sink, SimpleNamespace())
    packet = DummyPacket()

    packet_router.feed_rtp(packet)

    decoder = packet_router.decoders[packet.ssrc]
    assert decoder.processed == [packet]
    assert decoder.pushed == []
    assert len(sink.writes) == 1
    data, user = sink.writes[0]
    assert data.packet is packet
    assert user == "user"


def test_packet_router_buffers_opus_packets(monkeypatch):
    monkeypatch.setattr(router_module, "PacketDecoder", DummyDecoder)
    sink = DummySink(opus=True)
    packet_router = router_module.PacketRouter(sink, SimpleNamespace())
    packet = DummyPacket()

    packet_router.feed_rtp(packet)

    decoder = packet_router.decoders[packet.ssrc]
    assert decoder.pushed == [packet]
    assert decoder.processed == []
    assert sink.writes == []


class DummyGuild:
    member = SimpleNamespace(id=42)

    def get_member(self, member_id):
        if member_id == self.member.id:
            return self.member
        return None


class DummyClient:
    def __init__(self):
        self.guild = DummyGuild()
        self._connection = SimpleNamespace(ssrc_user_map={1: 42})
        self.dispatched = []

    def _dispatch_sink(self, event, member):
        self.dispatched.append((event, member))


def test_speaking_timer_handles_notify_before_thread_waits():
    client = DummyClient()
    timer = SpeakingTimer(SimpleNamespace(client=client))
    timer.speaking_timeout_delay = 0.01

    timer.notify(1)
    timer.start()

    deadline = time.perf_counter() + 1
    while time.perf_counter() < deadline:
        if ("member_speaking_stop", client.guild.member) in client.dispatched:
            break
        time.sleep(0.01)

    timer.stop()
    timer.join(timeout=1)

    assert ("member_speaking_start", client.guild.member) in client.dispatched
    assert ("member_speaking_stop", client.guild.member) in client.dispatched
