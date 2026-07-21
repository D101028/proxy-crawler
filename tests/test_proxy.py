import unittest

from src.net import quick_ping
from src.settings import *

class TestNet(unittest.TestCase):

    def setUp(self):
        return 

    def test_ping1(self):
        host = "8.8.8.8"
        timeout = 2
        latency_ms = quick_ping(host, timeout)
        print("Latency:", latency_ms)
    def test_ping2(self):
        host = "google.com"
        timeout = 2
        latency_ms = quick_ping(host, timeout)
        print("Latency:", latency_ms)
    
    def test_proxy1(self):
        pass 

if __name__ == '__main__':
    unittest.main()