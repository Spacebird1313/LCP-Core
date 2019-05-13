from lcp.core.interfaces.module import Module
from lcp.modules.camerafeed.camera_feed import CameraFeed
from lcp.modules.facedetector.face_detector import FaceDetector
import cv2 as cv
import _thread


class FrameViewer(Module):
    __name = "Frame Viewer"
    __version = "1.0"
    __dependencies = [CameraFeed]
    __optional_dependencies = [FaceDetector]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies, self.__optional_dependencies)
        self.__camera_feed = []
        self.__face_detector = []
        self.__frame_thread = []

    def install(self, modules):
        modules = super().install(modules)
        self.__camera_feed = modules['CameraFeed']

        try:
            self.__face_detector = modules['FaceDetector']
        except:
            # Optional module - skip
            pass

    def start(self):
        self.__frame_thread = _thread.start_new_thread(self.__run_viewer, ())

    def __run_viewer(self):
        while True:
            frame = self.__camera_feed.get_frame()

            if self.__face_detector:
                faces = self.__face_detector.get_detected_faces()
                for(x, y, w, h) in faces:
                    cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv.imshow(self.__name + ' - ' + self.__version, frame)

            if cv.waitKey(1) == ord("q"):
                pass
