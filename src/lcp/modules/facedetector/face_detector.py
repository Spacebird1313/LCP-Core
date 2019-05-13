from lcp.core.interfaces.module import Module
from lcp.modules.camerafeed.camera_feed import CameraFeed
import cv2 as cv
import _thread


class FaceDetector(Module):
    __name = "Face Detector"
    __version = "1.0"
    __dependencies = [CameraFeed]

    def __init__(self, config):
        super().__init__(self.__name, self.__version, self.__dependencies)
        self.__face_classifier_file = config.get('face_classifier', fallback='classifier.xml')
        self.__face_classifier = []
        self.__absolute_face_size = 0
        self.__tracked_faces = []
        self.__camera_feed = []
        self.__detector_thread = []

    def install(self, modules):
        modules = super().install(modules)
        self.__camera_feed = modules['CameraFeed']
        self.__face_classifier = cv.CascadeClassifier('..\\modules\\facedetector\\classifiers\\' + self.__face_classifier_file)

    def start(self):
        self.__detector_thread = _thread.start_new_thread(self.__detect_faces, ())

    def get_detected_faces(self):
        return self.__tracked_faces

    def __detect_faces(self):
        while True:
            frame = self.__camera_feed.get_frame()
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            gray_frame = cv.equalizeHist(gray_frame)

            if self.__absolute_face_size == 0:
                height, width = gray_frame.shape[:2]

                if float(height) * 0.2 > 0:
                    self.__absolute_face_size = int(height * 0.2)

            self.__tracked_faces = self.__face_classifier.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=2, minSize=(self.__absolute_face_size, self.__absolute_face_size))
