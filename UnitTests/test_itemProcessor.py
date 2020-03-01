from unittest import TestCase

from ServiceRunner.Classes import Item
from ServiceRunner.Processors import ItemProcessor


class TestItemProcessor(TestCase):
    def test_process_firstNone_assertItem(self):
        item_processor = ItemProcessor()
        item1 = item_processor.process([])
        item2 = Item(0, 0, -1, 0, 0, 0, 0, 0)

        self.AssertAttributes(item1, item2)

    def AssertAttributes(self, item1, item2):
        for attribute in item1.__dict__.keys():
            att1 = item1.__dict__[attribute]
            att2 = item2.__dict__[attribute]
            self.assertEqual(att1, att2)

    def test_process_secondNone_assertItem(self):
        item_processor = ItemProcessor()
        _ = item_processor.process([])
        item1 = item_processor.process([])
        item2 = Item(1, 0, -1, 0, 0, 0, 0, 0)
        self.AssertAttributes(item1, item2)

    def test_process_secondAfter_assertItem(self):
        item_processor = ItemProcessor()
        item0 = Item(5, 0, 3, 1, 100, 100, 100, 100)
        _ = item_processor.process([item0])
        item1 = item_processor.process([])
        item2 = Item(6, 0, 3, 1, 100, 100, 100, 100)
        self.AssertAttributes(item1, item2)
