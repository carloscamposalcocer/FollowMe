import logging
import os
import threading
import time
from os.path import join

from ServiceRunner.Camera import Camera
from ServiceRunner.Followers import SimpleFollower
from ServiceRunner.NeuralEngine import NetHandler, process_output
from ServiceRunner.Processors import ItemProcessor
from ServiceRunner.Tools import PathManager, ItemLogger, ImageSaver

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, config):
        self.net_handler = NetHandler(config.nn_config)
        self.target_label = config.nn_config.target_label
        self.follower = SimpleFollower()
        self.item_processor = ItemProcessor()
        self.keep_running = False
        self.resolution = (config.cam_width, config.cam_height)

    def close(self):
        self.follower.close()

    def work(self):
        abs_path = os.path.dirname(os.path.abspath(__file__))
        path_manager = PathManager(join(abs_path, "..", "Images"))
        path_manager.new_set()
        item_logger = ItemLogger(path_manager.log_path)
        saver = ImageSaver(path_manager.images_pattern)
        frame_number = 0
        cam = Camera(self.resolution)

        logger.info("Starting working loop")
        while self.keep_running:
            image = cam.read()
            saver.save(image)
            logger.debug(f"Image size = {image.shape}")
            self.net_handler.load(image)
            out = self.net_handler.infer()
            items = process_output(out, frame_number, time.time(), self.target_label)
            frame_number += 1
            item = self.item_processor.process(items)
            item_logger.log(item)
            if item:
                self.follower.follow(item)
        cam.close()
        logger.info("Stopping working loop")
        item_logger.close()
        self.follower.pause()


class MultithreadWorker:
    def __init__(self, config):
        # config = ServiceConfig.read_config(r"ServiceRunner/config.json")
        self.keep_running = False
        self.resolution = (config.cam_width, config.cam_height)
        self.follower = SimpleFollower()
        self.net_handler = NetHandler(config.nn_config)
        self.target_label = config.nn_config.target_label
        self.out = None
        self.image_available = threading.Event()
        self.output_available = threading.Event()

    def work(self):
        threading.Thread(target=self._infer_loop).start()
        item_processor = ItemProcessor()
        frame_number = 0
        abs_path = os.path.dirname(os.path.abspath(__file__))
        path_manager = PathManager(join(abs_path, "..", "Images"))
        path_manager.new_set()
        saver = ImageSaver(path_manager.images_pattern)
        item_logger = ItemLogger(path_manager.log_path)
        camera = Camera(self.resolution)
        time.sleep(2.0)
        image = camera.read()
        self.net_handler.load(image)
        saver.save(image)
        self.image_available.set()
        while self.keep_running:
            image = camera.read()
            blob = self.net_handler.preprocess_image(image)
            if not self.output_available.wait(10):
                break
            self.output_available.clear()
            self.net_handler.load_blob(blob)
            self.image_available.set()
            saver.save(image)
            items = process_output(self.out, frame_number, time.time(), self.target_label)
            frame_number += 1
            item = item_processor.process(items)
            item_logger.log(item)
            if item:
                self.follower.follow(item)

        self.keep_running = False
        self.image_available.set()
        self.follower.pause()
        item_logger.close()
        camera.close()

    def _infer_loop(self):
        while self.keep_running:
            if not self.image_available.wait(10):
                break
            self.image_available.clear()
            self.out = self.net_handler.infer()
            self.output_available.set()

    def close(self):
        self.follower.close()
