from lcp.core.interfaces.module import Module
from lcp.modules.servocontrol.servo_control import ServoControl
import csv
import time
import _thread


class AnimationPlayer(Module):
    __name = "Animation Player"
    __version = "1.0"
    __dependencies = [ServoControl]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__servo_control = None
        self.__animation_thread = []
        self.__FPS = 16.293
        self.__channel_priority = 1
        self.__interrupted = False
        self.__playing = 0

    def install(self, modules):
        modules = super().install(modules)
        self.__servo_control = modules['ServoControl']

    def start(self):
        pass

    def stop_animation(self):
        self.__interrupted = True

    def play_animation(self, file, blocking=False, priority=1, overwrite=True):
        if self.__playing > 0 and not overwrite:
            self.stop_animation()

        while self.__playing > 0 and not overwrite:
            time.sleep(.1)

        if blocking:
            self.__play_animation_thread(file, priority)
        else:
            self.__animation_thread = _thread.start_new_thread(self.__play_animation_thread, (file, priority))

    def is_animation_playing(self):
        return self.__playing > 0

    def __play_animation_thread(self, file, priority):
        self.__playing = self.__playing + 1
        self.__interrupted = False
        with open(file) as csv_file:
            motion_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            current_time = time.time()
            missed_time = 0
            frame_time = 1./self.__FPS
            for row in motion_reader:
                if missed_time > frame_time:
                    print("Frame Skipped (overtime:", str(missed_time - frame_time) + "s)")
                    missed_time -= frame_time
                    continue
                last_frame_time = current_time

                num_of_channels = len(row) - 1
                channel_index = 0
                for pos in row:
                    if channel_index >= num_of_channels:
                        break
                    elif int(pos) != -1:
                        self.__servo_control.set_channel_position(channel_index, int(pos), priority)

                    channel_index += 1

                current_time = time.time()
                sleep_time = frame_time - (current_time - last_frame_time) - missed_time

                if self.__interrupted:
                    for channel_index in range(num_of_channels):
                        self.__servo_control.release_channel_priority(channel_index, priority)

                    self.__playing = self.__playing - 1
                    return

                if sleep_time > 0:
                    time.sleep(sleep_time)
                    missed_time = 0
                else:
                    missed_time += (-sleep_time)

            # End of animation
            for channel_index in range(num_of_channels):
                self.__servo_control.release_channel_priority(channel_index, priority)

            self.__playing = self.__playing - 1
