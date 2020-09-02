#!/bin/python

from gotchaBot import Util
from datetime import datetime, timedelta
import unittest

class TestTime(unittest.TestCase):
    time1 = datetime(2020, 8, 29, 20, 30, 0, 0)  # outside interval
    time2 = datetime(2020, 8, 30, 20, 30, 0, 0)  # outside interval
    time3 = datetime(2020, 8, 30, 23, 30, 0, 0)  # outside interval
    time4 = datetime(2020, 8, 31, 15, 30, 20, 0)  # outside interval
    time5 = datetime(2020, 8, 31, 20, 30, 20, 0)  # inside interval
    time6 = datetime(2020, 8, 31, 23, 30, 20, 0)  # inside interval
    time7 = datetime(2020, 9, 1, 3, 30, 20, 0)  # inside interval
    time8 = datetime(2020, 9, 1, 14, 30, 20, 0)  # outside interval
    time9 = datetime(2020, 9, 1, 3, 30, 20, 0)  # inside interval
    time10 = datetime(2020, 9, 1, 4, 30, 42, 0)  # outside interval
    
    def test_inSlot(self):
        u = Util()
        self.assertFalse(u.isInTimeSlot(self.time1))
        self.assertFalse(u.isInTimeSlot(self.time2))
        self.assertFalse(u.isInTimeSlot(self.time3))
        self.assertFalse(u.isInTimeSlot(self.time4))
        self.assertTrue(u.isInTimeSlot(self.time5))
        self.assertTrue(u.isInTimeSlot(self.time6))
        self.assertFalse(u.isInTimeSlot(self.time7))
        self.assertFalse(u.isInTimeSlot(self.time8))
        self.assertFalse(u.isInTimeSlot(self.time9))
        self.assertFalse(u.isInTimeSlot(self.time10))

    def test_interaval(self):
        u = Util()
        #  self.assertEqual(u.calculateInterval(self.time2, self.time3), timedelta(hours=3))
        self.assertEqual(u.calculateInterval(self.time1, self.time2), timedelta(days=1))
        self.assertEqual(u.calculateInterval(self.time2, self.time3), timedelta())
        self.assertEqual(u.calculateInterval(self.time3, self.time4), timedelta(hours=16, seconds=20))
        self.assertEqual(u.calculateInterval(self.time4, self.time5), timedelta(hours=4, minutes=30, seconds=20))
        self.assertEqual(u.calculateInterval(self.time4, self.time6), timedelta(hours=7, minutes=30, seconds=20))
        #  self.assertEqual(u.calculateInterval(self.time4, self.time7), timedelta(hours=11, minutes=30, seconds=20))
        self.assertEqual(u.calculateInterval(self.time6, self.time10), timedelta(hours=2, minutes=29, seconds=40))


if __name__ == '__main__':
    unittest.main()
