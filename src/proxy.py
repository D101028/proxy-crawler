from datetime import datetime
from dataclasses import dataclass

from src.net import quick_ping
from src.settings import *

@dataclass()
class ProxyNode:
    protocol: str
    host: str
    port: int
    
    anonymity: str
    code: str | None
    country: str | None
    
    last_checked: datetime | None = None   # last checked time
    alive: bool | None = None              # availability of the node
    latency_ms: int | None = None          # ping latency (ms)
    response_ms: int | None = None         # response ms

    def get_url(self):
        return f"{self.protocol}://{self.host}:{self.port}"

    def test_node(self, 
        test_url: str = TEST_URL, 
        ping_timeout_ms: int = PING_TIMEOUT_MS, 
        response_timeout_ms: int = RESPONSE_TIMEOUT_MS
    ):
        # Test Ping
        latency_ms = quick_ping(self.host, PING_TIMEOUT_MS)
        if latency_ms < 0:
            self.last_checked = datetime.now()
            self.alive = False
            self.latency_ms = -1
            self.response_ms = -1
            return False
        # Test Proxy

        

