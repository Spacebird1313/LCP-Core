from lcp.core.interfaces.module import Module
import cv2 as cv
import numpy as np
import time
import _thread


class CameraFeed(Module):
    __name = "Camera Feed"
    __version = "1.0"

    def __init__(self, config):
        super().__init__(self.__name, self.__version)
        self.__camera_id = self.__parse_camera_id_config(config.get('camera_id', fallback='0'))
        self.__rotations = self.__parse_camera_rotation_config(config.get('camera_rotations', fallback=[]), len(self.__camera_id))
        self.__cameras = []
        self.__frame = None
        self.__camera_thread = None
        self.__cachedH = None
        self.__cachedTrim = None

    def install(self, modules):
        super().install(modules)
        self.__open_camera()

    def start(self):
        if len(self.__cameras) > 2:
            print("WARNING - Frame stitching in multi-camera setups is currently only supported for two cameras. Stitching first two streams...")

        self.__start_capture()

    def get_frame(self):
        while self.__frame is None:
            pass

        return self.__frame

    def __parse_camera_id_config(self, camera_id):
        try:
            parsed_camera_id = list(map(int, camera_id.split(",")))
        except:
            # Is a non numeric value - return as string
            parsed_camera_id = camera_id.split(",")

        return parsed_camera_id

    def __parse_camera_rotation_config(self, camera_rotation, number_of_cameras):
        parsed_camera_rotations = []

        try:
            parsed_camera_rotations = list(map(int, camera_rotation.split(",")))
        except:
            print("Could not parse camera rotation. Camera streams will not be rotated!")

        while len(parsed_camera_rotations) < number_of_cameras:
            parsed_camera_rotations.append(0)

        return parsed_camera_rotations

    def __open_camera(self):
        for camera_id in self.__camera_id:
            camera = cv.VideoCapture(camera_id)

            while not camera.isOpened():
                camera = cv.VideoCapture(camera_id)
                time.sleep(.5)

            self.__cameras.append(camera)

    def __start_capture(self):
        self.__camera_thread = _thread.start_new_thread(self.__capture_frame, ())

    def __capture_frame(self):
        while True:
            collected_frames = []
            for index, camera in enumerate(self.__cameras):
                ret, camera_frame = camera.read()

                if self.__rotations[index] is not 0:
                    camera_frame = self.__rotate_frame(camera_frame, self.__rotations[index])

                collected_frames.append(camera_frame)

            if len(collected_frames) > 1:
                stitched_frame = self.__stitch_frames(collected_frames)

                if stitched_frame is None:
                    print("Failed to stitch images of multiple camera streams!")
                    self.__frame = collected_frames[0]
                else:
                    self.__frame = stitched_frame
            else:
                self.__frame = collected_frames[0]

    def __rotate_frame(self, frame, angle):
        h, w = frame.shape[:2]
        cX, cY = (w // 2, h // 2)

        M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        return cv.warpAffine(frame, M, (nW, nH))

    def __stitch_frames(self, frames, ratio=0.75, reprojThresh=4.0):
        # for i in range(len(frames) - 1):
        for i in range(1):
            imageA = frames[i + 1]
            imageB = frames[i]

            if self.__cachedH is None:
                print("Calibrating multi-camera setup...")
                kpsA, featuresA = self.__detect_and_describe(imageA)
                kpsB, featuresB = self.__detect_and_describe(imageB)

                M = self.__match_keypoints(kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh)

                if M is None:
                    return None

                self.__cachedH = M[1]
                print("Calibration finished!")

            result = cv.warpPerspective(imageA, self.__cachedH, (imageA.shape[1] + imageB.shape[1], max(imageA.shape[0], imageB.shape[0])))
            result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB

            frames[i + 1] = result

        return self.__trim_frame(frames[len(frames) - 1])

    def __detect_and_describe(self, frame):
        descriptor = cv.xfeatures2d.SIFT_create()
        kps, features = descriptor.detectAndCompute(frame, None)

        kps = np.float32([kp.pt for kp in kps])

        return kps, features

    def __match_keypoints(self, kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh):
        matcher = cv.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []

        for m in rawMatches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))

        if len(matches) > 4:
            ptsA = np.float32([kpsA[i] for (_, i) in matches])
            ptsB = np.float32([kpsB[i] for (i, _) in matches])

            H, status = cv.findHomography(ptsA, ptsB, cv.RANSAC, reprojThresh)

            return matches, H, status

        return None

    def __trim_frame(self, frame):
        if self.__cachedTrim is None:
            left_trim = 0
            right_trim = 0
            top_trim = 0
            bottom_trim = 0

            for i in range(frame.shape[0]):
                if np.sum(frame[i]):
                    top_trim = i
                    break

            for i in range(frame.shape[0]):
                if np.sum(frame[frame.shape[0] - i - 1]):
                    bottom_trim = frame.shape[0] - i - 1
                    break

            for i in range(frame.shape[1]):
                if np.sum(frame[:, i:]):
                    left_trim = i
                    break

            for i in range(frame.shape[1]):
                if np.sum(frame[:, frame.shape[1] - i - 1]):
                    right_trim = frame.shape[1] - i - 1
                    break

            self.__cachedTrim = (top_trim, bottom_trim, left_trim, right_trim)

        return frame[self.__cachedTrim[0]:self.__cachedTrim[1], self.__cachedTrim[2]:self.__cachedTrim[3]]
