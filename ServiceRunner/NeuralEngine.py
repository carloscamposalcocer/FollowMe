import os
import time
from os.path import abspath, join

import cv2
import numpy as np
from ServiceRunner.Classes import Item
import logging

logger = logging.getLogger(__name__)


class NetHandler:
    def __init__(self, nn_config):
        """

        :type nn_config: ServiceRunner.ConfigReader.NNConfig
        """
        logger.info("Init NetHandler")
        root_path = abspath(join(__file__, "../.."))
        self.image_size = (nn_config.image_width, nn_config.image_height)
        xml_file = join(root_path, nn_config.model_xml_path)
        bin_file = xml_file.replace(".xml", ".bin")
        logger.info(f"loading model: {xml_file}")
        if not os.path.exists(xml_file):
            raise Exception(f"Path not found {xml_file}")
        try:
            logger.info("readnet")
            self.net = cv2.dnn.readNet(bin_file, xml_file)
            logger.info("settarget")
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
            logger.info("preprocess")
            blob = self.preprocess_image(np.zeros((300, 300, 3), dtype=np.uint8))
            logger.info("blob")
            self.net.setInput(blob)
            logger.info("forward")
            self.net.forward()
            logger.debug("Inter stick Initialized")
        except cv2.error:
            logger.warning("Downgrading to CPU")
            self.net = cv2.dnn.readNet(bin_file, xml_file)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        self.blob = None
        self.frame = None

    def infer(self):
        t = time.time()
        out = self.net.forward()
        print(f"infertime = {time.time() - t}")
        return out

    def load(self, image):
        self.frame = image
        self.blob = self.preprocess_image(image)
        self.net.setInput(self.blob)

    def load_blob(self, blob):
        self.net.setInput(blob)

    def preprocess_image(self, image):
        return cv2.dnn.blobFromImage(image, size=self.image_size, ddepth=cv2.CV_8U)


def process_output(out, frame, timestamp, target_label=None):
    labels = out[0, 0, :, 1]
    confidences = out[0, 0, :, 2]
    boxes = out[0, 0, :, 3:7]
    items = []
    for conf, box, label in zip(confidences, boxes, labels):
        if conf < 0.3:
            continue
        if target_label is not None and target_label != label:
            continue
        items.append(Item(frame, timestamp, label, conf, *box))
    return items
