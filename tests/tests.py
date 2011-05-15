import unittest
from time import sleep
from afd import AccrualFailureDetector


class TestAccrualFailureDetector(unittest.TestCase):

    def setUp(self):
        self.fd = AccrualFailureDetector()

    def test_failure_detection(self):
        host = "192.168.0.39"
        self.fd.heartbeat(host)
        sleep(1)
        self.fd.heartbeat(host)
        sleep(0.1)
        self.fd.heartbeat(host)
        self.assertTrue(self.fd.isAlive(host))
        sleep(7)
        self.assertTrue(self.fd.isDead(host))


if __name__ == '__main__':
    unittest.main()