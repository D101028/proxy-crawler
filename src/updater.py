import concurrent.futures
import time
import json
from datetime import datetime
from typing import Iterable, Any

from src.mod import CrawlerTemplate, crawler_classes
from src.mylog import log_info
from src.net import quick_ping, test_proxy
from src.proxy import ProxyNode, ProxyStatus
from src.settings import *

# 測試節點
def test_node(
    node: ProxyNode, 
    test_url: str = TEST_URL, 
    ping_timeout_ms: int = PING_TIMEOUT_MS, 
    response_timeout_ms: int = RESPONSE_TIMEOUT_MS
) -> ProxyStatus:
    
    # 測試 Ping
    latency_ms = quick_ping(node.host, max(1, ping_timeout_ms // 1000))
    if latency_ms < 0:
        return ProxyStatus(alive=False, latency_ms=-1, response_ms=-1)
    
    # 測試 Proxy
    response_ms = test_proxy(
        node.protocol, node.host, node.port, 
        test_url, response_timeout_ms / 1000, 
        node.username, node.password
    )
    if response_ms < 0:
        return ProxyStatus(alive=False, latency_ms=latency_ms, response_ms=-1)
    
    return ProxyStatus(alive=True, latency_ms=latency_ms, response_ms=response_ms)


class ProxyChecker:
    def __init__(self, nodes: Iterable[ProxyNode] | None = None) -> None:
        null_status = ProxyStatus.get_null_status()
        self._node_pool: dict[ProxyNode, ProxyStatus] = {
            node: null_status for node in (nodes if nodes is not None else [])}

        self._valid_node_pool: dict[ProxyNode, ProxyStatus] | None = None
        self._last_checked: datetime | None = None

    def append_node(self, node: ProxyNode, check: bool = False) -> None:
        if check:
            status = test_node(node)
            self._node_pool[node] = status
            if status.alive:
                if self._valid_node_pool is None:
                    self._valid_node_pool = {node: status}
                else:
                    self._valid_node_pool[node] = status
            return 
        self._node_pool[node] = ProxyStatus.get_null_status()
    
    def get_status(self, node: ProxyNode) -> ProxyStatus | None:
        return self._node_pool.get(node)

    def get_pool(self) -> dict[ProxyNode, ProxyStatus]:
        return self._node_pool

    def pop_node(self, node: ProxyNode) -> ProxyStatus | None:
        return self._node_pool.pop(node, None)

    def clear_nodes(self) -> None:
        self._node_pool.clear()

    def merge_nodes(self, nodes: Iterable[ProxyNode]) -> None:
        null_status = ProxyStatus.get_null_status()
        for node in nodes:
            self._node_pool.setdefault(node, null_status)

    def check_and_merge_nodes(self, nodes: Iterable[ProxyNode], max_workers: int = MAX_WORKERS, drop_invalid: bool = True) -> None:
        if self._valid_node_pool is None:
            self._valid_node_pool = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 建立 Future -> Node 映射
            future_to_node = {
                executor.submit(test_node, node): node for node in nodes
            }

            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    # 獲取 test_node 回傳的全新 ProxyStatus 快照
                    result: ProxyStatus = future.result()
                except Exception as e:
                    # 避免單一線程崩潰導致整個 check_all 中斷
                    result = ProxyStatus(alive=False, latency_ms=-1, response_ms=-1)
                
                if drop_invalid and not result.alive:
                    continue

                # 更新總池子的最新狀態
                self._node_pool[node] = result
                if result.alive:
                    self._valid_node_pool[node] = result

    def check_all(self, max_workers: int = MAX_WORKERS, drop_invalid: bool = False) -> dict[ProxyNode, ProxyStatus]:
        valid_node_pool: dict[ProxyNode, ProxyStatus] = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 建立 Future -> Node 映射
            future_to_node = {
                executor.submit(test_node, node): node for node in self._node_pool
            }

            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    # 獲取 test_node 回傳的全新 ProxyStatus 快照
                    result: ProxyStatus = future.result()
                except Exception as e:
                    # 避免單一線程崩潰導致整個 check_all 中斷
                    result = ProxyStatus(alive=False, latency_ms=-1, response_ms=-1)

                # 不論成功或失敗，都必須更新總池子（self._node_pool）的最新狀態
                self._node_pool[node] = result

                # 如果存活，則歸類到有效池子
                if result.alive:
                    valid_node_pool[node] = result
        
        # 更新全域統計資訊
        self._valid_node_pool = valid_node_pool
        self._last_checked = datetime.now()

        # 處理丟棄無效節點
        if drop_invalid:
            # 複製一份新的
            self._node_pool = dict(valid_node_pool) 
        
        return valid_node_pool

    def get_valid_nodes(self) -> dict[ProxyNode, ProxyStatus]:
        if self._valid_node_pool is None:
            return self.check_all()
        else:
            return self._valid_node_pool

    def get_nodes_dict(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for node, status in self._node_pool.items():
            d: Any = node.to_dict()
            d.update(status.to_dict())
            out.append(d)
        return out

class ProxyUpdater:
    def __init__(self, nodes_checker: ProxyChecker | None = None) -> None:
        self._nodes_checker: ProxyChecker = ProxyChecker() if nodes_checker is None else nodes_checker

        self._crawler_instances: list[CrawlerTemplate] = [c() for c in crawler_classes]

        self._last_fetched: datetime | None = None

    def _update_file(self) -> None:
        proxies = self._nodes_checker.get_nodes_dict()
        with open(OUTPUT_JSON_PATH, mode="w") as fp:
            json.dump(proxies, fp)

    def run(self, loop_interval: int = CHECK_INTERVAL * 60) -> None:
        """
        Start the checking loop. 

        :param int loop_interval: the waiting seconds for the next loop
        """
        while True:
            log_info("Updating proxies...")
            for crawler in self._crawler_instances:
                nodes = crawler.fetch()
                self._nodes_checker.merge_nodes(nodes)
                self._nodes_checker.check_all(drop_invalid=True)
            self._update_file()

            # Get the during time 
            if self._last_fetched is None:
                during_time = 0
            else:
                during_time = (datetime.now() - self._last_fetched).seconds
            # Update last fetched time
            self._last_fetched = datetime.now()

            log_info("Proxies updated.")

            time.sleep(max(loop_interval - during_time, 0))
