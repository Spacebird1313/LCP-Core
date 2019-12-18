from lcp.core.interfaces.module import Module
from lcp.modules.facedetector.face_detector import FaceDetector
from lcp.modules.servocontrol.servo_control import ServoControl
import _thread
import time
import math


class FaceTracker(Module):
    __name = "Face Tracker"
    __version = "1.0"
    __dependencies = [FaceDetector, ServoControl]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__channel_priority_value = 250
        self.__horizontal_channel = int(config.get('horizontal_channel', fallback=0))
        self.__horizontal_min = int(config.get('horizontal_min', fallback=None))
        self.__horizontal_max = int(config.get('horizontal_max', fallback=None))
        self.__horizontal_offset = int(config.get('horizontal_offset', fallback=0))
        self.__horizontal_scale = int(config.get('horizontal_scale', fallback=1))
        self.__vertical_channel = int(config.get('vertical_channel', fallback=1))
        self.__vertical_min = int(config.get('vertical_min', fallback=None))
        self.__vertical_max = int(config.get('vertical_max', fallback=None))
        self.__vertical_offset = int(config.get('vertical_offset', fallback=0))
        self.__vertical_scale = int(config.get('vertical_scale', fallback=1))
        self.__face_timout = 1.5
        self.__max_face_deviation = 25
        self.__face_detector = None
        self.__servo_control = None
        self.__tracker_thread = None

    def install(self, modules):
        modules = super().install(modules)
        self.__face_detector = modules['FaceDetector']
        self.__servo_control = modules['ServoControl']

    def start(self):
        self.__tracker_thread = _thread.start_new_thread(self.__run_tracker, ())

    def __run_tracker(self):
        last_face_detected = None
        last_face_time = 0

        while True:
            faces = self.__face_detector.get_detected_faces()
            face_found = False

            for(x, y, w, h) in faces:
                face_center = ((x+(w/2)), (y+(h/2)))

                if last_face_detected:
                    deviation = math.sqrt((last_face_detected[0] - face_center[0])**2 + (last_face_detected[1] - face_center[1])**2)

                    if deviation > self.__max_face_deviation:
                        continue

                face_found = True
                last_face_detected = face_center
                last_face_time = time.time()
                break

            if not face_found and ((time.time() - last_face_time) > self.__face_timout):
                last_face_detected = None

            if last_face_detected:
                horizontal_turn = last_face_detected[0] - (self.__face_detector.get_frame_dimensions()[0]/2)
                horizontal_position = (self.__horizontal_max - self.__horizontal_min)/2 + self.__horizontal_min + self.__horizontal_scale * horizontal_turn + self.__horizontal_offset
                vertical_turn = last_face_detected[1] - (self.__face_detector.get_frame_dimensions()[1]/2)
                vertical_position = (self.__vertical_max - self.__vertical_min)/2 + self.__vertical_min + self.__vertical_scale * vertical_turn + self.__vertical_offset
                self.__servo_control.set_channel_position(self.__horizontal_channel, horizontal_position, self.__channel_priority_value)
                self.__servo_control.set_channel_position(self.__vertical_channel, vertical_position, self.__channel_priority_value)
            else:
                self.__servo_control.release_channel_priority(self.__horizontal_channel, self.__channel_priority_value)
                self.__servo_control.release_channel_priority(self.__vertical_channel, self.__channel_priority_value)
