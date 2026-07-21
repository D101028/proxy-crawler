import random
import subprocess
import time
import unittest

from src.net import quick_ping, test_proxy
from src.proxy import ProxyNode
from src.settings import *

class TestNet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. 定義測試用代理節點的參數
        cls.protocol = "socks5"
        cls.host = "127.0.0.1"
        cls.port = random.randint(20000, 65534)
        cls.username = "yaju"
        cls.password = "1145141919810"

        # 2. gost 啟動指令
        # 建立一個有帳密認證的 SOCKS5 代理伺服器
        gost_path = "C:/gost/gost.exe"
        gost_args = f"-L={cls.protocol}://{cls.username}:{cls.password}@:{cls.port}"
        
        cls.cmd = [gost_path, gost_args]

        # 3. 啟動背景程序
        # 使用 stdout/stderr PIPE 避免測試畫面被 gost 的 log 洗版
        cls.gost_process = subprocess.Popen(
            cls.cmd,
            stdout=subprocess.DEVNULL,  # 直接丟棄，不佔用緩衝區
            stderr=subprocess.DEVNULL,
        )
        
        # 給 gost 一小段時間初始化監聽埠，避免測試跑太快噴 ConnectionRefusedError
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        # 4. 結束時正確清理
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

class TestProxy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. 定義測試用代理節點的參數
        cls.protocol = "socks5"
        cls.host = "127.0.0.1"
        cls.port = random.randint(20000, 65534)
        cls.username = "yaju"
        cls.password = "1145141919810"

        # 2. gost 啟動指令
        # 建立一個有帳密認證的 SOCKS5 代理伺服器
        gost_path = "C:/gost/gost.exe"
        gost_args = f"-L={cls.protocol}://{cls.username}:{cls.password}@:{cls.port}"
        
        cls.cmd = [gost_path, gost_args]

        # 3. 啟動背景程序
        # 使用 stdout/stderr PIPE 避免測試畫面被 gost 的 log 洗版
        cls.gost_process = subprocess.Popen(
            cls.cmd,
            stdout=subprocess.DEVNULL,  # 直接丟棄，不佔用緩衝區
            stderr=subprocess.DEVNULL,
        )
        
        # 給 gost 一小段時間初始化監聽埠，避免測試跑太快噴 ConnectionRefusedError
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        # 4. 結束時正確清理
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
            None, None, None, 
            self.username, self.password
        )

        # 驗證代理節點是否測試成功
        self.assertTrue(node.test_node())

if __name__ == '__main__':
    unittest.main()