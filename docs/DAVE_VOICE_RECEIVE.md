# DAVE Voice Receive Implementation

Documentation for the DAVE (Discord Audio Video Encryption) voice receive fixes applied
to py-cord.

---

## What is DAVE?

DAVE stands for Discord Audio Video Encryption. It is Discord's end-to-end encryption
layer for voice and video channels.

- Enforced globally by Discord as of March 2, 2026. All voice connections now require
  DAVE support; bots that do not handle DAVE decryption will receive encrypted
  (unintelligible) audio.
- Uses MLS (Messaging Layer Security, RFC 9420) for group key management. Each voice
  session establishes an MLS group, and keys are ratcheted as members join and leave.
- Built on the `davey` Rust library, which exposes Python bindings. `davey` handles MLS
  state, key derivation, and the actual encrypt/decrypt operations on audio frames.

---

## Architecture: Two-Layer Decryption

Voice packets on the wire are protected by two independent encryption layers:

| Layer               | Encryption                                                       | Purpose                                                                                 |
| ------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Layer 1 (transport) | NaCl -- `xsalsa20_poly1305` or `aead_xchacha20_poly1305_rtpsize` | Hop-by-hop transport encryption between client and Discord media server                 |
| Layer 2 (E2E)       | DAVE -- MLS group keys via `davey`                               | End-to-end encryption between voice participants; Discord servers cannot read the audio |

### Send path

```
opus frame
  -> DAVE encrypt (Layer 2, E2E)
  -> NaCl encrypt (Layer 1, transport)
  -> wire (RTP packet)
```

### Receive path

```
wire (RTP packet)
  -> NaCl decrypt (Layer 1, transport)
  -> DAVE decrypt (Layer 2, E2E)
  -> opus frame
  -> PCM (decoded by libopus)
```

The key insight is that DAVE operates on **opus-encoded frames**, not on decoded PCM
audio. This ordering constraint was the root cause of several bugs.

---

## Bugs Found and Fixed

Six bugs were identified and fixed in the voice receive pipeline.

### 1. Double DAVE decryption (opus.py)

**Problem:** `_decode_packet()` called `dave.decrypt()` on PCM data _after_ the opus
decode step. DAVE operates on opus-encoded frames, so decrypting PCM data produced
garbage or threw errors.

**Root cause:** The DAVE decrypt call was placed in the wrong function. Decryption
should happen in `decrypt_rtp()` (before opus decode), not in `_decode_packet()` (after
opus decode).

**Fix:** Removed the DAVE decrypt call from `_decode_packet()`. DAVE decryption now only
happens in `decrypt_rtp()`, which runs before the opus decode step.

---

### 2. decrypt_rtp() fallback bug (reader.py)

**Problem:** When DAVE was not ready or the user was not in the `ssrc_user_map`,
`packet.decrypted_data` was never set. The function returned `None`, which crashed
downstream code that expected a packet with valid data.

**Root cause:** The non-DAVE fallback path did not assign `packet.decrypted_data`.

**Fix:** Always set `packet.decrypted_data` from the transport-decrypted payload. The
DAVE layer is additive -- if DAVE is unavailable, the transport-decrypted data is still
valid audio (it just was not end-to-end encrypted).

---

### 3. Sink missing methods (sinks/core.py)

**Problem:** The new voice receive system expected three methods/attributes on the
`Sink` base class: `is_opus()`, `walk_children()`, and `__sink_listeners__`. The old
`Sink` class did not define them.

**Root cause:** The voice receive rewrite introduced new protocols that the base `Sink`
class was never updated to satisfy.

**Fix:** Added `is_opus()`, `walk_children()`, and `__sink_listeners__` to the `Sink`
base class with sensible defaults.

---

### 4. Sink not initialized (voice/client.py)

**Problem:** `start_recording()` never called `sink.init(self)`. As a result,
`sink.client` was `None`, which caused an `AssertionError` in `opus.py` when the sink
tried to access its client reference.

**Root cause:** The `sink.init()` call was missing from the recording setup sequence.

**Fix:** Added `sink.init(self)` in `start_recording()` before creating the
`AudioReader`.

---

### 5. Router passing VoiceData instead of bytes (router.py)

**Problem:** `sink.write()` received `VoiceData` objects instead of raw audio bytes. Old
sinks expect `(bytes, user)` as arguments and cannot handle `VoiceData`.

**Root cause:** The new router emitted `VoiceData` wrapper objects, but the sink
interface was never updated to accept them.

**Fix:** Extract `data.pcm` from the `VoiceData` object before passing it to
`sink.write()`.

---

### 6. JitterBuffer too small and strict ordering (buffer.py)

**Problem:** `max_size` was set to 10. At 50 packets per second (20ms opus frames), the
buffer fills in 200ms. Additionally, the buffer enforced strict sequential ordering on
the consumer side, causing it to stall whenever a packet arrived out of order.

**Result:** 73% packet loss. Audio sounded accelerated and chopped because most frames
were dropped.

**Fix:** Increased `max_size` to 200, providing approximately 4 seconds of headroom.
Removed the strict sequential ordering requirement so the consumer processes packets as
they arrive rather than waiting for gaps to fill.

---

## Additional Fixes

Beyond the six primary bugs, several reliability improvements were made:

- **Router thread crash handling:** A crash in the router thread previously killed the
  entire recording session (the `finally` block called auto-stop). Removed the auto-stop
  from the `finally` block so that transient errors do not tear down the whole pipeline.

- **Error in callback isolation:** An error in a single packet callback previously
  stopped all future packet processing. Errors are now caught and cleared so processing
  continues.

- **Opus decode error resilience:** Opus decode errors are now caught and produce
  silence frames instead of crashing the receive loop.

- **AEAD rtpsize extension header offset:** The code used a hardcoded offset of 8 for
  reading the RTP extension header. The fix uses the actual offset derived from the
  header, which varies depending on the extensions present.

---

## How to Test

1. Create a Discord bot with voice permissions (connect, speak, and use voice activity).
2. Install py-cord from this branch.
3. Use `start_recording()` with any `Sink` implementation (for example, `WaveSink`).
4. Have the bot join a voice channel and record audio from other participants.
5. Verify the output by transcribing the recorded audio with Whisper or another
   speech-to-text tool. Clean, intelligible transcriptions confirm that both decryption
   layers and the decode pipeline are working correctly.

---

## Configuration

| Parameter               | Default   | Notes                                                                                                                                                |
| ----------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `JitterBuffer.max_size` | 200       | Number of packets the buffer can hold. At 50 packets/sec this is 4 seconds of headroom. Increase for high-latency or lossy connections.              |
| DAVE encryption         | Automatic | No configuration needed. DAVE negotiation is handled by the voice gateway during session setup. The `davey` library manages MLS state transparently. |
