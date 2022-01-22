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
import os
import wave

from .core import Filters, Sink, default_filters
from .errors import WaveSinkError


class WaveSink(Sink):
    """A Sink "stores" all the audio data.
    
    Used for .wav(wave) files.
    
    .. versionadded:: 2.1
    
    Parameters
    ----------
    encoding: :class:`string`
        The encoding to use. Valid types include wav, mp3, and pcm (even though it's not an actual encoding).
    output_path: :class:`string`
        A path to where the audio files should be output.
    
    Raises
    ------
    ClientException
        An invalid encoding type was specified.
        Audio may only be formatted after recording is finished.
    """

    def __init__(self, *, output_path="", filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        self.encoding = "wav"
        self.file_path = output_path
        self.vc = None
        self.audio_data = {}

    def format_audio(self, audio):
        if self.vc.recording:
            raise WaveSinkError(
                "Audio may only be formatted after recording is finished."
            )
        with open(audio.file, "rb") as pcm:
            data = pcm.read()
            pcm.close()

            wav_file = audio.file.split(".")[0] + ".wav"
            with wave.open(wav_file, "wb") as f:
                f.setnchannels(self.vc.decoder.CHANNELS)
                f.setsampwidth(self.vc.decoder.SAMPLE_SIZE // self.vc.decoder.CHANNELS)
                f.setframerate(self.vc.decoder.SAMPLING_RATE)
                f.writeframes(data)
                f.close()
        os.remove(audio.file)
        audio.on_format(self.encoding)