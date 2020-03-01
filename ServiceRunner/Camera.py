from abc import ABCMeta, abstractmethod, ABC
from threading import Thread
from time import sleep
import logging

logger = logging.getLogger(__name__)

try:
    import picamera
    import picamera.array
    from picamera.array import PiRGBArray
    from picamera import PiCamera

    camera_type = "raspi"
except ModuleNotFoundError:
    import cv2

    camera_type = "cv2"


class CommonCamera(metaclass=ABCMeta):
    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def close(self):
        pass


class Cv2Camera(CommonCamera):
    def __init__(self):
        logger.info("Init OpenCv Camera")
        self.cap = cv2.VideoCapture(0)

    def read(self):
        _, image = self.cap.read()
        return cv2.flip(image, 1)

    def close(self):
        logger.info("Closing OpenCv Camera")
        self.cap.release()


class Camera(CommonCamera):
    def __init__(self, resolution):
        logger.debug("Init Camera")
        if camera_type == "raspi":
            self.camera = RaspiCamera2(resolution)
        else:
            self.camera = Cv2Camera()

    def read(self):
        return self.camera.read()

    def close(self):
        self.camera.close()


class RaspiCamera(CommonCamera):
    def __init__(self):
        logger.info("Init Raspi Camera")
        self.cam = picamera.PiCamera()
        self.cam.vflip = True
        self.cam.resolution = (720, 480)
        print(f"Picamera init a resolution {self.cam.resolution}")
        self.stream = picamera.array.PiRGBArray(self.cam)
        sleep(0.1)

    def read(self):
        self.cam.capture(self.stream, 'bgr', use_video_port=True)
        self.stream.seek(0)
        self.stream.truncate()
        return self.stream.array

    def close(self):
        logger.info("Closing Raspi Camera")
        self.stream.close()
        self.cam.close()


class RaspiCamera2(CommonCamera):
    def close(self):
        self.vs.stop()

    def __init__(self, resolution):
        logger.info("Init Raspi2 Camera")
        self.vs = PiVideoStream(resolution=resolution).start()

    def read(self):
        return self.vs.read()


class PiVideoStream:
    def __init__(self, resolution=(720, 480), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.vflip = True
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr", use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
