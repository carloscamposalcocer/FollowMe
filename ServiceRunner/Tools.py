import csv
import os
import re
import cv2
import numpy as np
import logging
from ServiceRunner.Classes import Relation, Item

logger = logging.getLogger(__name__)


def iou(item1, item2):
    """

    :type item2: Item
    :type item1: Item
    """
    intersect_w = _interval_overlap([item1.xmin, item1.xmax], [item2.xmin, item2.xmax])
    intersect_h = _interval_overlap([item1.ymin, item1.ymax], [item2.ymin, item2.ymax])

    intersect = intersect_w * intersect_h

    w1, h1 = item1.xmax - item1.xmin, item1.ymax - item1.ymin
    w2, h2 = item2.xmax - item2.xmin, item2.ymax - item2.ymin

    union = w1 * h1 + w2 * h2 - intersect

    return float(intersect) / union


def _interval_overlap(interval_a, interval_b):
    x1, x2 = interval_a
    x3, x4 = interval_b

    if x3 < x1:
        if x4 < x1:
            return 0
        else:
            return min(x2, x4) - x1
    else:
        if x2 < x3:
            return 0
        else:
            return min(x2, x4) - x3


def items_iou(items1, items2):
    relations = []
    for i in range(len(items1)):
        for j in range(len(items2)):
            relation = Relation(iou(items1[i], items2[j]), (i, j))
            relations.append(relation)
    relations.sort(key=lambda x: x.score, reverse=True)
    return relations


def draw_item(frame, item, color=(0, 255, 0)):
    (h, w) = frame.shape[:2]
    if item.xmax == item.xmin == item.ymin == item.ymax == 0:
        return
    (startX, startY, endX, endY) = (int(item.xmin * w), int(item.ymin * h), int(item.xmax * w), int(item.ymax * h))

    # draw the prediction on the frame
    label = "{:.2f}%".format(item.score * 100)
    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
    y = startY - 15 if startY - 15 > 15 else startY + 15
    cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


class ItemLogger:
    def __init__(self, save_path):
        logger.info(f"Init {self.__class__.__name__}")
        self.file = open(save_path, 'w')
        fieldnames = ['frame', 'time', 'label', 'score', 'xmin', 'ymin', 'xmax', 'ymax']
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames, lineterminator="\n")
        self.writer.writeheader()

    def log(self, item):
        """
        :type item: ServiceRunner.Classes.Item
        """
        self.writer.writerow(item.__dict__)

    def close(self):
        logger.info(f"Closing {self.__class__.__name__}")
        self.file.close()


def read_items(read_path):
    with open(read_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        items = []
        for row in reader:
            for k, v in row.items():
                row[k] = float(v)
            item = Item(**row)
            items.append(item)
    return items


class ImageSaver:
    def __init__(self, file_pattern):
        self.filename, self.file_ext = os.path.splitext(file_pattern)
        dirname = os.path.dirname(file_pattern)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.i = 0

    def save(self, image):
        filename = f"{self.filename}{self.i}{self.file_ext}"
        logger.debug(f"Saving {filename}")
        cv2.imwrite(filename, image)
        self.i += 1


class PathManager(object):
    def __init__(self, root):
        self.set_path = None
        self.images_pattern = None
        self.log_path = None
        self.root = root
        if not os.path.exists(self.root):
            os.makedirs(self.root)

    def use_last(self):
        set_id = self.get_last_id()
        self.use_set_id(set_id)

    def use_set_id(self, set_id):
        self.set_path = os.path.join(self.root, f"Set{set_id}")
        self.images_pattern = os.path.join(self.set_path, "Image.jpeg")
        self.log_path = os.path.join(self.set_path, "Boxes.csv")

    def new_set(self):
        last_id = self.get_last_id()
        if last_id is None:
            set_id = 0
        else:
            set_id = last_id + 1
        self.use_set_id(set_id)
        os.makedirs(self.set_path)

    def get_last_id(self):
        dirs = os.listdir(self.root)
        if not dirs: return None
        set_id = 0
        for dir in dirs:
            session = re.findall("Set\d+", dir)
            if session:
                if len(session) > 1:
                    raise ValueError("Path should only contain 1 Set Word")
                session = int(session[0].lstrip("Set"))
                set_id = max(session, set_id)
        return set_id

    def list_images(self):
        files = os.listdir(self.set_path)
        images = [file for file in files if re.findall("Image\d+.jpeg", file)]
        images.sort(key=self.get_id)
        images = [os.path.join(self.set_path, image) for image in images]
        return images

    @staticmethod
    def get_id(file_name):
        sessions = re.findall("\d+", file_name)
        if not sessions:
            raise Exception("There is no number in path")
        if len(sessions) > 1:
            raise ValueError("Path should only contain 1 number")
        return int(sessions[0])


def center_distance(item):
    """

    :type item: Item
    """
    x = (item.xmin + item.xmax) / 2
    y = (item.ymin + item.ymax) / 2
    return np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
