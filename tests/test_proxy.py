import os
import random
import subprocess
import time
import unittest

from src.net import quick_ping, test_proxy
from src.proxy import ProxyNode, test_node, ProxyStatus, ProxyChecker, ProxyUpdater
from src.settings import *

def create_host(
    protocol: str, port: int, 
    username: str | None, password: str | None
) -> subprocess.Popen[bytes]:
    # gost 啟動指令
    # 建立一個有帳密認證的 SOCKS5 代理伺服器
    gost_path = "C:/gost/gost.exe"
    if username is None or password is None:
        gost_args = f"-L={protocol}://:{port}"
    else:
        gost_args = f"-L={protocol}://{username}:{password}@:{port}"
    
    cmd = [gost_path, gost_args]

    # 啟動背景程序
    # 使用 stdout/stderr PIPE 避免測試畫面被 gost 的 log 洗版
    gost_process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,  # 直接丟棄，不佔用緩衝區
        stderr=subprocess.DEVNULL,
    )

    return gost_process

class TestNet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 定義測試用代理節點的參數
        cls.protocol = "socks5"
        cls.host = "127.0.0.1"
        cls.port = random.randint(20000, 65535)
        cls.username = "yaju"
        cls.password = "1145141919810"

        # 建立伺服器
        cls.gost_process = create_host(cls.protocol, cls.port, cls.username, cls.password)
        
        # 給 gost 一小段時間初始化監聽埠，避免測試跑太快噴 ConnectionRefusedError
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        # 結束時正確清理
        if hasattr(cls.gost_process, "terminate"):
            cls.gost_process.terminate()  # 發送 SIGTERM
            try:
                cls.gost_process.wait(timeout=2)  # 等待程序完全結束
            except subprocess.TimeoutExpired:
                cls.gost_process.kill()  # 超時則強行殺死 (SIGKILL)

    def test_ping1(self):
        host = "8.8.8.8"
        timeout = 2
        latency_ms = quick_ping(host, timeout)
        print("Latency:", latency_ms)
        self.assertNotEqual(latency_ms, -1)
    def test_ping2(self):
        host = "google.com"
        timeout = 2
        latency_ms = quick_ping(host, timeout)
        print("Latency:", latency_ms)
        self.assertNotEqual(latency_ms, -1)
    
    def test_proxy1(self):
        latency_ms = test_proxy(
            self.protocol, self.host, self.port, TEST_URL, RESPONSE_TIMEOUT_MS // 1000, 
            self.username, self.password
        )
        print("Latency:", latency_ms)
        self.assertTrue(latency_ms != -1)

class TestProxyNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 定義測試用代理節點的參數
        cls.protocol = "socks5"
        cls.host = "127.0.0.1"
        cls.port = random.randint(20000, 65535)
        cls.username = "yaju"
        cls.password = "1145141919810"

        # 建立伺服器
        cls.gost_process = create_host(cls.protocol, cls.port, cls.username, cls.password)
        
        # 給 gost 一小段時間初始化監聽埠，避免測試跑太快噴 ConnectionRefusedError
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        # 結束時正確清理
        if hasattr(cls.gost_process, "terminate"):
            cls.gost_process.terminate()  # 發送 SIGTERM
            try:
                cls.gost_process.wait(timeout=2)  # 等待程序完全結束
            except subprocess.TimeoutExpired:
                cls.gost_process.kill()  # 超時則強行殺死 (SIGKILL)

    def test_proxy_node(self):
        # 使用 setUp 建立好的參數來實例化物件
        node = ProxyNode(
            self.protocol, self.host, self.port, 
            username=self.username, password=self.password
        )

        # 驗證代理節點是否測試成功
        self.assertTrue(test_node(node).alive)

class TestProxyChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 定義測試用代理節點數量
        TEST_NUM = 4

        # 建立節點伺服器
        cls.nodes: list[tuple[ProxyNode, subprocess.Popen[bytes]]] = []
        start_port = random.randint(10000, 65535-TEST_NUM)
        for i in range(TEST_NUM):
            node = ProxyNode(
                "socks5", "127.0.0.1", start_port + i, 
                username=os.urandom(8).hex(), password=os.urandom(8).hex()
            )
            p = create_host(
                node.protocol, node.port, node.username, node.password
            )
            cls.nodes.append((node, p))
        
        time.sleep(TEST_NUM ** 0.5)

    @classmethod
    def tearDownClass(cls):
        for node, p in cls.nodes:
            if hasattr(p, 'terminate'):
                p.terminate()
                try:
                    p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    p.kill()

    def test_check_all(self):
        node1, node2, node3 = self.nodes[0][0], self.nodes[1][0], self.nodes[2][0]
        checker = ProxyChecker((node1, node2, node3))

        checker.check_all()

        valid_nodes = checker.get_valid_nodes()
        for _, status in valid_nodes.items():
            self.assertTrue(status.alive)

    def test_append(self):
        node1, node2, node3 = self.nodes[0][0], self.nodes[1][0], self.nodes[2][0]
        checker = ProxyChecker((node1, node2))

        checker.check_all()

        # 測試 check=False
        checker.append_node(node3, check=False)

        status = checker.get_status(node3)
        self.assertIsNotNone(status)
        assert status is not None

        self.assertIsNone(status.alive)

        # drop node3
        checker.pop_node(node3)

        # 測試 check=True
        checker.append_node(node3, check=True)
        status = checker.get_status(node3)
        self.assertIsNotNone(status)
        assert status is not None

        self.assertTrue(status.alive)

    

if __name__ == '__main__':
    unittest.main()