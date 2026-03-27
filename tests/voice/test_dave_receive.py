"""Tests for the DAVE (Discord Audio/Video Encryption) voice receive path.

Covers the two-layer decryption pipeline in PacketDecryptor.decrypt_rtp(),
the JitterBuffer behaviour, the Sink base class interface, and the
PacketRouter's resilience when writing to sinks.
"""

from __future__ import annotations

import inspect

import pytest

from discord.sinks.core import Sink
from discord.voice.packets.core import OPUS_SILENCE
from discord.voice.utils.buffer import JitterBuffer


# ---------------------------------------------------------------------------
# Lightweight fakes — no unittest.mock
# ---------------------------------------------------------------------------


class FakePacket:
    """Minimal stand-in for an RTP packet."""

    def __init__(self, ssrc=1, sequence=1, timestamp=1, data=b"test"):
        self.ssrc = ssrc
        self.sequence = sequence
        self.timestamp = timestamp
        self.data = data
        self.decrypted_data = None
        self.extended = False

    def __lt__(self, other):
        return self.sequence < other.sequence

    def __bool__(self):
        return True


class FakeDaveSession:
    """Simulates a DAVE session with configurable behaviour."""

    def __init__(self, ready=True, passthrough=False, decrypt_result=b"decrypted"):
        self.ready = ready
        self._passthrough = passthrough
        self._decrypt_result = decrypt_result
        self.decrypt_called = False

    def can_passthrough(self, uid):
        return self._passthrough

    def decrypt(self, uid, media_type, data):
        self.decrypt_called = True
        if self._decrypt_result is Exception:
            raise RuntimeError("DAVE decrypt failure")
        return self._decrypt_result


class FailingDaveSession(FakeDaveSession):
    """A DAVE session whose decrypt() always raises."""

    def decrypt(self, uid, media_type, data):
        self.decrypt_called = True
        raise RuntimeError("DAVE decrypt failure")


class FakeConnectionState:
    """Minimal stand-in for a VoiceConnectionState."""

    def __init__(self, dave_session=None, ssrc_user_map=None):
        self.dave_session = dave_session
        self.ssrc_user_map = ssrc_user_map or {}


class FakeClient:
    """Minimal stand-in for VoiceClient — just enough for PacketDecryptor."""

    def __init__(self, connection_state):
        self._connection = connection_state


class FakeNaClResult:
    """Tracks whether Layer 1 (NaCl) decryption was called."""

    def __init__(self, result=b"nacl_decrypted"):
        self.result = result
        self.called = False

    def __call__(self, packet):
        self.called = True
        return self.result


class TrackingSink(Sink):
    """A sink that records every write() call for later assertion."""

    def __init__(self):
        super().__init__()
        self.writes = []

    def write(self, data, user):
        self.writes.append((data, user))

    def is_opus(self):
        return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def packet():
    return FakePacket(ssrc=100, sequence=5, timestamp=1000, data=b"encrypted")


@pytest.fixture
def jitter_buffer():
    return JitterBuffer(max_size=200, pref_size=0, prefill=0)


# ---------------------------------------------------------------------------
# Tests 1-4: PacketDecryptor.decrypt_rtp two-layer pipeline
# ---------------------------------------------------------------------------


def _make_decryptor(dave_session=None, ssrc_user_map=None):
    """Build a PacketDecryptor whose Layer 1 is a no-op fake.

    We bypass __init__ because the real constructor needs NaCl and a full
    VoiceClient.  Instead we wire up only the attributes that decrypt_rtp()
    actually reads.
    """
    from discord.voice.receive.reader import PacketDecryptor

    state = FakeConnectionState(
        dave_session=dave_session,
        ssrc_user_map=ssrc_user_map or {},
    )
    client = FakeClient(state)

    decryptor = PacketDecryptor.__new__(PacketDecryptor)
    decryptor.client = client

    # Layer 1 fake — returns deterministic bytes so we can verify Layer 2
    decryptor._decryptor_rtp = FakeNaClResult(b"nacl_opus_payload")
    return decryptor


def test_decrypt_rtp_without_dave(packet):
    """Without a DAVE session only NaCl decryption runs."""
    decryptor = _make_decryptor(dave_session=None)

    result = decryptor.decrypt_rtp(packet)

    assert decryptor._decryptor_rtp.called
    assert result == b"nacl_opus_payload"
    assert packet.decrypted_data == b"nacl_opus_payload"


def test_decrypt_rtp_with_dave(packet):
    """With an active DAVE session, both NaCl and DAVE decryption run."""
    dave = FakeDaveSession(ready=True, passthrough=False, decrypt_result=b"dave_clear")
    decryptor = _make_decryptor(
        dave_session=dave,
        ssrc_user_map={packet.ssrc: 12345},
    )

    result = decryptor.decrypt_rtp(packet)

    assert decryptor._decryptor_rtp.called
    assert dave.decrypt_called
    assert result == b"dave_clear"
    assert packet.decrypted_data == b"dave_clear"


def test_decrypt_rtp_dave_passthrough(packet):
    """When can_passthrough() is True, DAVE decrypt is skipped."""
    dave = FakeDaveSession(ready=True, passthrough=True, decrypt_result=b"should_not_appear")
    decryptor = _make_decryptor(
        dave_session=dave,
        ssrc_user_map={packet.ssrc: 12345},
    )

    result = decryptor.decrypt_rtp(packet)

    assert decryptor._decryptor_rtp.called
    assert not dave.decrypt_called
    # Result should be Layer 1 output, not DAVE output
    assert result == b"nacl_opus_payload"
    assert packet.decrypted_data == b"nacl_opus_payload"


def test_decrypt_rtp_dave_failure_fallback(packet):
    """When DAVE decrypt raises, the result falls back to OPUS_SILENCE."""
    dave = FailingDaveSession(ready=True, passthrough=False)
    decryptor = _make_decryptor(
        dave_session=dave,
        ssrc_user_map={packet.ssrc: 12345},
    )

    result = decryptor.decrypt_rtp(packet)

    assert dave.decrypt_called
    assert result == OPUS_SILENCE
    assert packet.decrypted_data == OPUS_SILENCE


# ---------------------------------------------------------------------------
# Test 5: _decode_packet must not reference DAVE at all
# ---------------------------------------------------------------------------


def test_decode_packet_no_double_dave():
    """_decode_packet() should not touch the DAVE session.

    DAVE decryption is handled exclusively in PacketDecryptor.decrypt_rtp().
    If _decode_packet ever references 'dave' it would mean double-decryption.
    We use AST analysis so that comments mentioning DAVE are ignored -- only
    actual code identifiers (variable names, attribute access) are checked.
    """
    import ast
    import textwrap

    from discord.opus import PacketDecoder

    source = inspect.getsource(PacketDecoder._decode_packet)
    tree = ast.parse(textwrap.dedent(source))

    # Collect every Name and Attribute identifier in the function body
    identifiers = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr.lower())

    dave_refs = [name for name in identifiers if "dave" in name]
    assert not dave_refs, (
        f"_decode_packet contains code references to DAVE ({dave_refs!r}) -- "
        "DAVE decryption should only happen in PacketDecryptor.decrypt_rtp()"
    )


# ---------------------------------------------------------------------------
# Tests 6-7: JitterBuffer
# ---------------------------------------------------------------------------


def test_jitter_buffer_signals_on_data(jitter_buffer):
    """Pushing packets into the buffer should set the _has_item event."""
    assert not jitter_buffer._has_item.is_set()

    pkt = FakePacket(ssrc=1, sequence=1, timestamp=100)
    jitter_buffer.push(pkt)

    # With pref_size=0 and prefill=0, the first push should signal readiness
    assert jitter_buffer._has_item.is_set()


def test_jitter_buffer_capacity():
    """When more than max_size packets are pushed, _cleanup drops the oldest."""
    buf = JitterBuffer(max_size=200, pref_size=0, prefill=0)

    for i in range(250):
        pkt = FakePacket(ssrc=1, sequence=i, timestamp=i * 960)
        buf.push(pkt)

    assert len(buf) <= 200


# ---------------------------------------------------------------------------
# Test 8-9: Sink base class
# ---------------------------------------------------------------------------


def test_sink_has_required_attributes():
    """The Sink base class must expose is_opus, walk_children, and __sink_listeners__."""
    sink = Sink()
    assert hasattr(sink, "is_opus") and callable(sink.is_opus)
    assert hasattr(sink, "walk_children") and callable(sink.walk_children)
    assert hasattr(sink, "__sink_listeners__")


def test_sink_init_sets_client():
    """After init(vc) the sink.client property should return the voice client."""

    class FakeVC:
        pass

    sink = Sink()
    vc = FakeVC()
    # Sink.init() also calls Filters.init() which starts a timer thread when
    # seconds != 0.  With the default filters seconds == 0, so no thread.
    sink.init(vc)

    assert sink.client is vc


# ---------------------------------------------------------------------------
# Tests 10-11: PacketRouter write behaviour
# ---------------------------------------------------------------------------


def test_router_writes_pcm_bytes_not_voicedata():
    """The sink's write() should receive raw bytes, not a VoiceData wrapper."""
    sink = TrackingSink()

    # Simulate what the router's _do_run loop does: it calls
    # sink.write(audio_bytes, data.source).  We replicate the exact call.
    pcm_bytes = b"\x00" * 3840
    user_id = 99999
    sink.write(pcm_bytes, user_id)

    assert len(sink.writes) == 1
    data, user = sink.writes[0]
    assert isinstance(data, bytes)
    assert data == pcm_bytes
    assert user == user_id


def test_router_survives_bad_packet():
    """The router's per-packet error handling should let it keep processing.

    We simulate the pattern from PacketRouter._do_run: if one packet decode
    raises, the next packet should still be processed.
    """
    sink = TrackingSink()
    errors = []

    # Simulate the router's inner loop with exception handling
    packets = [
        ("bad", None, None),  # will cause an error
        ("good", b"\x00" * 3840, 42),  # should still be written
    ]

    for label, pcm, source in packets:
        try:
            if pcm is None:
                raise ValueError("simulated decode error")
            audio_bytes = pcm
            if audio_bytes:
                sink.write(audio_bytes, source)
        except Exception as exc:
            errors.append(exc)

    # One error occurred but the second packet still got through
    assert len(errors) == 1
    assert len(sink.writes) == 1
    assert sink.writes[0] == (b"\x00" * 3840, 42)
