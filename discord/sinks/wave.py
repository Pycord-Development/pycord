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

import io
import wave

from .core import Sink
from .errors import WaveSinkError


class WaveSink(Sink):
    """A special sink for .wav(wave) files.

    .. versionadded:: 2.0
    """

    def __init__(self, *, filters=None):
        self.encoding = "wav"
        super().__init__(filters=filters)

    def format_audio(self, audio):
        """Formats the recorded audio.

        Raises
        ------
        WaveSinkError
            Audio may only be formatted after recording is finished.
        WaveSinkError
            Formatting the audio failed.
        """
        if self.vc.is_recording():
            raise WaveSinkError(
                "Audio may only be formatted after recording is finished."
            )
        pcm_data = audio.file.read()
        out = io.BytesIO()

        with wave.open(out, "wb") as f:
            # Voice receive decode output is 48kHz, 16-bit, stereo PCM.
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(48000)
            f.writeframes(pcm_data)

        out.seek(0)
        audio.file = out
        audio.on_format(self.encoding)



