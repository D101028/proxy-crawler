import os
import random
import subprocess
import time
import unittest

from src.browser import Browser
from src.mod import GeonodeCrawler
from src.settings import *


class TestGeonodeCrawler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crawler = GeonodeCrawler()

    # @classmethod
    # def tearDownClass(cls):
    #     ...

    def test_browser(self):
        response = self.crawler.browser.get()
        raw_data = response.json()
        self.assertIn('data', raw_data)
        raw_proxies = raw_data.get('data')
        self.assertIsInstance(raw_proxies, list)
        self.assertNotEqual(len(raw_proxies), 0)
        print(raw_proxies[0])

    def test_fetch(self):
        nodes = self.crawler.fetch()
        print(nodes[:10])

if __name__ == "__main__":
    unittest.main()
