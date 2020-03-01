import time

import numpy as np
import logging
from ServiceRunner.Classes import Item
from ServiceRunner.Tools import iou, items_iou

logger = logging.getLogger(__name__)


class IouProcessor(object):
    def __init__(self):
        self.item = None

    def process(self, items):
        if not items:
            raise Exception("List should not be empty")
        if self.item is None:
            self.item = items[0]
        else:
            ious = [iou(item, self.item) for item in items]
            index = np.argmax(ious)
            self.item = items[index]
        return self.item


class ItemProcessor(object):
    def __init__(self):
        logger.info(f"Init {self.__class__.__name__}")
        self.item = Item(frame=-1, time=time.time(), label=-1)
        self.item_persistance = 3
        self.iou_processor = IouProcessor()
        self.last_detection = 0
        self.prob_threshold = 0.5

    def process(self, items):
        items = [item for item in items if item.score > self.prob_threshold]
        if not items:
            if self.item.frame + 1 - self.last_detection <= self.item_persistance:
                self.item = Item(self.item.frame + 1,
                                 self.item.time,
                                 self.item.label,
                                 self.item.score,
                                 self.item.xmin,
                                 self.item.ymin,
                                 self.item.xmax,
                                 self.item.ymax)
            else:
                self.item = Item(frame=self.item.frame + 1, time=time.time(), label=-1)
        else:
            self.item = self.iou_processor.process(items)
            self.last_detection = self.item.frame
        logger.debug(f"New Item {self.item}")
        return self.item

    def process_old(self, items):
        items.sort(key=lambda x: x.score, reverse=True)
        if not items:
            return self.item
        if self.item is None:
            self.item = items[0]
            return self.item
        relations = items_iou([self.item], items)
        if relations:
            print(relations)
            self.item = items[relations[0].pair[1]]
        return self.item

    def offset_item(self, delta):
        self.item.xmin = self.item.xmin - delta[0]
        self.item.xmax = self.item.xmax - delta[0]
        self.item.ymin = self.item.ymin - delta[1]
        self.item.ymax = self.item.ymax - delta[1]
