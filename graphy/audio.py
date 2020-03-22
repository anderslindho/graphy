import pyaudio
import numpy as np
from collections import deque


class AudioEngine:

    def __init__(self, sample_size=pyaudio.paInt16, channels=1, sample_rate=44100, chunk=1024):
        self.sample_format = sample_size
        self.channels = channels
        self._sample_rate = sample_rate
        self.chunk = chunk

        self.data = np.empty(self.chunk * self.channels)
        self.frames = deque()
        self.frame_time_delta = 0
        self.last_callback_time = 0
        self.latency = 0

        self.interface = pyaudio.PyAudio()
        self.stream = self.interface.open(
            format=self.sample_format,
            channels=self.channels,
            rate=self._sample_rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self.callback
        )

    def is_active(self):
        return self.stream.is_active()

    def callback(self, in_data, frame_count, time_info, status):
        current_time, input_time = time_info["current_time"], time_info["input_buffer_adc_time"]
        self.latency = current_time - input_time
        self.frame_time_delta = current_time - self.last_callback_time
        self.last_callback_time = current_time

        self.data = np.frombuffer(in_data, dtype=np.int16)
        self.frames.append(np.sum(self.data))
        return in_data, pyaudio.paContinue

    def get_latency(self):
        """in msec"""
        return round(self.latency * 1000, 2)

    def get_frame_time(self):
        """in msec"""
        return round(self.frame_time_delta * 1000, 2)

    def get_sample(self):
        return self.data

    def get_sample_len(self):
        return self.chunk * self.channels

    def get_sample_magnitude(self):
        return np.sum(self.data)

    def get_sample_log(self):
        return np.array(self.frames)

    def get_padded_sample_log(self):
        if len(self.get_sample_log()) >= (self.chunk * self.channels):
            return self.get_sample_log()[-(self.chunk * self.channels):]
        else:
            return np.pad(
                self.get_sample_log(),
                [(self.chunk * self.channels) - len(self.get_sample_log()), 0],
                "constant", constant_values=0
            )

    def get_fft_sample(self):
        fft = np.fft.fft(self.data)
        fft = np.fft.fftshift(np.abs(fft))
        return fft  # TODO: accentuate values

    def get_test_fft(self):
        fft = np.fft.fft(self.data)
        fft = np.abs(fft[0:self.chunk]) * 2 / (256 * self.chunk)
        return fft

    @property
    def sample_rate(self):
        return self._sample_rate

    def shutdown(self):
        self.stream.close()
        self.pya.terminate()

