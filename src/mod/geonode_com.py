
from .template import CrawlerTemplate
from src.browser import Browser
from src.mylog import log_info, log_error
from src.proxy import ProxyNode
from src.settings import *

API_URL = "https://proxylist.geonode.com/api/proxy-list?page=1&limit=500&sort_by=responseTime&sort_type=asc"

class GeonodeCrawler(CrawlerTemplate):
    def __init__(self) -> None:
        super().__init__()
        self.browser: Browser = Browser(
            API_URL, 
            headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT, max_retry=DEFAULT_MAX_RETRY)

    def fetch(self) -> list[ProxyNode]:
        try:
            log_info("正在從 Geonode 抓取 Proxy 列表...")
            response = self.browser.get()
            response.raise_for_status()
            raw_proxies = response.json().get('data')
        except Exception as e:
            log_error(f"無法抓取 API 資料: {e}")
            return []

        # Create ProxyNode list
        nodes: list['ProxyNode'] = []
        for proxy_info in raw_proxies:
            ip = proxy_info.get("ip")
            port = proxy_info.get("port")
            protocols = proxy_info.get("protocols", ["http"])
            anonymity = proxy_info.get("anonymityLevel")
            code = proxy_info.get("country")

            # 取得主要協定 (例如 http, https, socks5)
            protocol = protocols[0].lower() if protocols else "http"
            node = ProxyNode(protocol, ip, port, anonymity=anonymity, code=code)
            nodes.append(node)

        return nodes


