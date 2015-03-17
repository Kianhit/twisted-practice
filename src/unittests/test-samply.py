from twisted.python import log
import unittest
class DemoTest(unittest.TestCase):
    def test_failWithLog(self):
        try:
            1 / 0
        except:
            log.err()