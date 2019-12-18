from lcp.core.interfaces.module import Module
import time
import pyaudio
import _thread


class AudioRecorder(Module):
    __name = "Audio Recorder"
    __version = "1.0"

    def __init__(self, config):
        super().__init__(self.__name, self.__version)
        self.__audio_source = config.get('audio_source', fallback=None)
        self.__audio_format = pyaudio.paInt16
        self.__audio_frame_length = []
        self.__sample_rate = []
        self.__audio_stream = []
        self.__recorder_thread = []
        self.__callbacks = []

    def install(self, modules):
        super().install(modules)

        paudio = pyaudio.PyAudio()
        self.__audio_stream = paudio.open(rate=16000, channels=1, frames_per_buffer=512, format=self.__audio_format, input=True, input_device_index=self.__audio_source, stream_callback=self.__audio_callback, start=False)

    def start(self):
        self.__start_recording()

    def register_callback(self, callback):
        self.__callbacks.append(callback)

    def __start_recording(self):
        self.__recorder_thread = _thread.start_new_thread(self.__capture_sample, ())

    def __audio_callback(self, in_data, frame_count, time_info, status):
        for callback in self.__callbacks:
            callback(in_data, frame_count, time_info, status)

        return in_data, pyaudio.paContinue

    def __capture_sample(self):
        self.__audio_stream.start_stream()

        while True:
            time.sleep(.1)

    def __parse_audio_source_config(self, audio_source):
        if audio_source is None:
            return None

        try:
            audio_source_parsed = int(audio_source)
        except:
            raise Exception('Invalid audio source \'', audio_source, '\' provided! Must be an integer index value.')

        return audio_source_parsed
