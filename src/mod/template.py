
from src.browser import Browser
from src.proxy import ProxyNode

class CrawlerTemplate:
    def __init__(self) -> None:
        self.browser: Browser

    def fetch(self) -> list[ProxyNode]:
        return []


