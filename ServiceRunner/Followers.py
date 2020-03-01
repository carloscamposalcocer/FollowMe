from time import sleep
from ServiceRunner.SerialCom import Ardu
import logging
import numpy as np
logger = logging.getLogger(__name__)


def f(x):
    return 4 * np.sign(x)*abs(x ** 2)


class SimpleFollower:
    def __init__(self):
        self.target_height = 0.4
        self.turning_time = 4
        self.search_speed = 25
        self.search_sequence_delay = 20

        self.max_speed = 100
        logger.info(f"Init {self.__class__.__name__}")
        self.active = True
        self.last_detection = 0
        try:
            self.ardu = Ardu()
        except:
            self.active = False
            logger.warning("Using Fake Arduino")

    def follow(self, item):
        if item.label == -1:  # No detection
            self.ardu.send(0, 0)
            elapsed_time = item.time - self.last_detection
            if elapsed_time > self.search_sequence_delay:
                self.search(elapsed_time)
            return
        self.last_detection = item.time
        x = (item.xmin + item.xmax) / 2 - 0.5  # [-0.5, 0.5]
        h = (item.ymax - item.ymin)
        forward_speed = - (self.target_height - h) * 1500
        forward_speed = min(max(forward_speed, -self.max_speed), self.max_speed)
        lservo = forward_speed - f(x) * 200
        rservo = forward_speed + f(x) * 200

        lservo = self.constrain_speed(lservo)
        rservo = min(max(rservo, -self.max_speed), self.max_speed)

        if self.active:
            self.ardu.send(lservo, rservo)
        else:
            pass

    def close(self):
        if self.active:
            self.ardu.close()
        else:
            logger.warning(f"Fake closing")

    def pause(self):
        logger.info("Pausing Arduino")
        if self.active:
            self.ardu.send(0, 0)
        else:
            logger.warning("Fake pausing")

    def search(self, elapsed_time):
        mode = int(elapsed_time / self.turning_time) % 4
        if mode == 0:
            self.ardu.send(100, 25)
        elif mode == 1:
            self.ardu.send(-100, -25)
        elif mode == 2:
            self.ardu.send(25, 100)
        elif mode == 3:
            self.ardu.send(-25, -100)

    def constrain_speed(self, speed):
        return min(max(speed, -self.max_speed), self.max_speed)


class Ffollower:
    def __init__(self, start_pos, xlim, ylim, max_speed):
        logger.info(f"Init {self.__class__.__name__}")
        self.max_speed = max_speed
        self.ylim = ylim
        self.xlim = xlim
        self.size = (720, 480)
        try:
            self.ardu = Ardu()
            self.pos_x = start_pos[0]
            self.pos_y = start_pos[1]
            self.ardu.send(self.pos_x, self.pos_y)
            sleep(0.3)
            self.x_calibration = 17 / 20  # microsteps/pixels
            self.y_calibration = 19 / 20
            self.working = True
        except:
            self.working = False

    def follow(self, item):
        x = (item.xmin + item.xmax) / 2 - 0.5  # [-0.5, 0.5]
        y = (item.ymin + item.ymax) / 2 - 0.5
        x = x * self.size[0]  # [-size/2, +size/2]
        y = y * self.size[1]
        if self.working:
            old_pos = (self.pos_x, self.pos_y)
            self.pos_x += min(x * self.x_calibration, self.max_speed[0])
            self.pos_y -= min(y * self.y_calibration, self.max_speed[1])
            self.pos_x = max(min(self.pos_x, self.xlim[1]), self.xlim[0])
            self.pos_y = max(min(self.pos_y, self.ylim[1]), self.ylim[0])
            delta = (self.pos_x - old_pos[0], self.pos_y - old_pos[1])
            print(f"Best box: {x * self.size[0]}  {y * self.size[1]} -> {delta[0]}  {delta[1]}")
            self.ardu.send(self.pos_x, self.pos_y)
            delta = (delta[0] / self.size[0], delta[1] / self.size[1])
            return delta
        else:
            print(f"Fake going to {x} {y}")
            return 0, 0

        self.size = (360, 240)
        self.ardu = Ardu()

    def follow(self, item):
        x = (item.xmin + item.xmax) / 2 - 0.5  # [-0.5, 0.5]
        y = (item.ymin + item.ymax) / 2 - 0.5
        lservo = -y * 400 - x * 100
        rservo = -y * 400 + x * 100
        print(f"Going to ->l:{lservo} r:{rservo}")
        self.ardu.send(lservo, rservo)

    def close(self):
        self.ardu.close()

# class Follower:
#     def __init__(self, start_pos, xlim, ylim, max_speed):
#         self.max_speed = max_speed
#         self.ylim = ylim
#         self.xlim = xlim
#         self.size = (360, 240)
#         try:
#             self.ardu = Ardu()
#             self.pos_x = start_pos[0]
#             self.pos_y = start_pos[1]
#             self.ardu.send(self.pos_x, self.pos_y)
#             sleep(0.3)
#             self.x_calibration = 17 / 20  # microsteps/pixels
#             self.y_calibration = 19 / 20
#             self.working = True
#         except:
#             self.working = False
#
#     def follow(self, item):
#         x = (item.xmin + item.xmax) / 2 - 0.5  # [-0.5, 0.5]
#         y = (item.ymin + item.ymax) / 2 - 0.5
#         x = x * self.size[0]  # [-size/2, +size/2]
#         y = y * self.size[1]
#         if self.working:
#             old_pos = (self.pos_x, self.pos_y)
#             self.pos_x += min(x * self.x_calibration, self.max_speed[0])
#             self.pos_y -= min(y * self.y_calibration, self.max_speed[1])
#             self.pos_x = max(min(self.pos_x, self.xlim[1]), self.xlim[0])
#             self.pos_y = max(min(self.pos_y, self.ylim[1]), self.ylim[0])
#             delta = (self.pos_x - old_pos[0], self.pos_y - old_pos[1])
#             print(f"Best box: {x * self.size[0]}  {y * self.size[1]} -> {delta[0]}  {delta[1]}")
#             self.ardu.send(self.pos_x, self.pos_y)
#             delta = (delta[0] / self.size[0], delta[1] / self.size[1])
#             return delta
#         else:
#             print(f"Fake going to {x} {y}")
#             return 0, 0
