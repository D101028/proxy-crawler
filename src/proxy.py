from datetime import datetime
from dataclasses import dataclass

from src.net import quick_ping, test_proxy
from src.settings import *

@dataclass()
class ProxyNode:
    protocol: str
    host: str
    port: int
    
    anonymity: str | None
    code: str | None
    country: str | None

    username: str | None = None             # username for auth
    password: str | None = None             # password for auth
    
    # Info after testing
    last_checked: datetime | None = None    # last checked time
    alive: bool | None = None               # availability of the node
    latency_ms: int | None = None           # ping latency (ms)
    response_ms: int | None = None          # response ms

    def get_url(self):
        if self.username is None or self.password is None:
            return f"{self.protocol}://{self.host}:{self.port}"
        else:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"

    def test_node(self, 
        test_url: str = TEST_URL, 
        ping_timeout_ms: int = PING_TIMEOUT_MS, 
        response_timeout_ms: int = RESPONSE_TIMEOUT_MS
    ) -> bool:
        # Test Ping
        latency_ms = quick_ping(self.host, max(1, ping_timeout_ms // 1000))
        if latency_ms < 0:
            self.last_checked = datetime.now()
            self.alive = False
            self.latency_ms = -1
            self.response_ms = -1
            return False
        
        # Test Proxy
        response_ms = test_proxy(
            self.protocol, self.host, self.port, 
            test_url, response_timeout_ms / 1000, 
            self.username, self.password
        )
        if response_ms < 0:
            self.last_checked = datetime.now()
            self.alive = False
            self.latency_ms = latency_ms
            self.response_ms = -1
            return False
        
        return True

