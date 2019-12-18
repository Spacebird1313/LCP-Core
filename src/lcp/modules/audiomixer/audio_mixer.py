from lcp.core.interfaces.module import Module
from lcp.modules.audiomixer.audio_channel import AudioChannel
import sounddevice as sd
import time
import _thread


class AudioMixer(Module):
    __name = "Audio Mixer"
    __version = "1.0"
    __dependencies = []

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__front_channels = []
        self.__back_channels = []
        self.__audio_stream = None
        self.__audio_thread = None
        self.__front_audio_buffer = []
        self.__back_audio_buffer = []
        self.__audio_buffer = []
        self.__audio_callbacks = []
        self.__end_callbacks = []

    def install(self, modules):
        self.__audio_stream = sd.RawOutputStream(samplerate=16000, dtype='int16', channels=1, blocksize=0)
        self.register_audio_callback(self.__audio_stream.write)

    def start(self):
        if not self.__audio_stream.active:
            self.__audio_stream.start()

        self.__audio_thread = _thread.start_new_thread(self.__play_streams, ())

    def create_front_channel(self, name, sample_rate):
        new_channel = AudioChannel(self, 0, name, sample_rate)
        self.__front_channels.append(new_channel)

        return new_channel

    def create_back_channel(self, name, sample_rate):
        new_channel = AudioChannel(self, 0, name, sample_rate)
        self.__back_channels.append(new_channel)

        return new_channel

    def register_audio_callback(self, callback):
        self.__audio_callbacks.append(callback)

    def register_end_callback(self, callback):
        self.__end_callbacks.append(callback)

    def __play_streams(self):
        while True:
            for channel in self.__front_channels:
                buffer = channel.get_buffer()
                sample = bytearray()

                #if len(buffer) > int(3200/2):
                #    sample[:] = buffer[0:int(3200/2)-1]
                #    buffer[:] = buffer[int(3200/2):len(buffer)-1]
                #else:
                #    sample[:] = buffer
                #    buffer[:] = bytearray()

                sample[:] = buffer
                buffer[:] = bytearray()

                if len(sample) > 0:
                    try:
                        self.__notify_audio_callbacks(sample)
                    except Exception as e:
                        print("Failed to process audio in mixer callback: ", e)
                else:
                    self.__notify_end_callbacks()
                    time.sleep(0.001)

    def __notify_audio_callbacks(self, sample):
        for callback in self.__audio_callbacks:
            callback(sample)

    def __notify_end_callbacks(self):
        for callback in self.__end_callbacks:
            callback()

    def write(self, buf):
        """Write bytes to the stream."""
        underflow = self.__audio_stream.write(buf)
        if underflow:
            print('SoundDeviceStream write underflow (size:',
                  len(buf), ')')
        return len(buf)

    def flush(self):
        pass
        # if self.__audio_stream.active and self.__flush_size > 0:
        #    self.__audio_stream.write(b'\x00' * self.__flush_size)
