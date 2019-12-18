from lcp.core.interfaces.module import Module
from lcp.modules.audiomixer.audio_mixer import AudioMixer
from lcp.modules.servocontrol.servo_control import ServoControl
import numpy as np
import struct


class MouthSynchronizer(Module):
    __name = "Mouth Synchronizer"
    __version = "1.0"
    __dependencies = [AudioMixer, ServoControl]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__mouth_channel = int(config.get('mouth_channel', fallback=0))
        self.__mouth_min = int(config.get('mouth_min', fallback=0))
        self.__mouth_max = int(config.get('mouth_max', fallback=100))
        self.__mouth_range = self.__mouth_max - self.__mouth_min
        self.__mouth_channel_priority = 500
        self.__audio_mixer = None
        self.__servo_control = None

    def install(self, modules):
        modules = super().install(modules)
        self.__servo_control = modules['ServoControl']
        self.__audio_mixer = modules['AudioMixer']
        self.__audio_mixer.register_audio_callback(self.__mouth_sync)
        self.__audio_mixer.register_end_callback(self.__stop_mouth_sync)

    def start(self):
        pass

    def __mouth_sync(self, sample):
        abs_max = 2**16/2
        values = struct.unpack('!%sh' % (len(sample)//2), sample)
        average_value = abs(np.average(values))

        rel_value = average_value / abs_max

        amplified_value = min(rel_value * 20, 1)

        mouth_position = int(self.__mouth_min + (self.__mouth_range * amplified_value))

        self.__servo_control.set_channel_position(self.__mouth_channel, mouth_position, self.__mouth_channel_priority)

    def __stop_mouth_sync(self):
        self.__servo_control.release_channel_priority(self.__mouth_channel, self.__mouth_channel_priority)
