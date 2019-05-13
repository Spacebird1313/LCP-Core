from lcp.core.interfaces.module import Module
import cv2 as cv
import time
import _thread


class CameraFeed(Module):
    __name = "Camera Feed"
    __version = "1.0"

    def __init__(self, config):
        super().__init__(self.__name, self.__version)
        self.__camera = []
        self.__frame = None
        self.__camera_thread = []

    def install(self, modules):
        super().install(modules)
        self.__open_camera()

    def start(self):
        self.__start_capture()

    def get_frame(self):
        while self.__frame is None:
            pass

        return self.__frame

    def __open_camera(self):
        self.__camera = cv.VideoCapture(0)

        while not self.__camera.isOpened():
            self.__camera = cv.VideoCapture(0)
            time.sleep(.5)

    def __start_capture(self):
        self.__camera_thread = _thread.start_new_thread(self.__capture_frame, ())

    def __capture_frame(self):
        while True:
            ret, self.__frame = self.__camera.read()
