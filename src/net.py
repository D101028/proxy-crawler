import time
from ping3 import ping

import requests

from src.mylog import *

def quick_ping(host, timeout: int) -> int:
    """
    Ping 指定的 IP 或網域並返回連線狀態

    :param host: 網域名稱 (如 'google.com') 或 IP 位址 (如 '8.8.8.8')
    :param timeout: 超時秒數
    :return: Nonnegative integer (成功，延遲 ms) 或 -1 (失敗)
    """
    # ping() 會回傳延遲時間（秒）。若失敗則回傳 False，超時則回傳 None
    response_time = ping(host, timeout=timeout)
    
    if response_time is None or response_time is False:
        return -1
    else:
        return int(response_time * 1000)

def test_proxy(
        protocol: str, host: str, port: int, 
        test_url: str, timeout: int | float, 
        username: str | None = None, password: str | None = None) -> int:
    """
    以指定 PROXY 測試訪問 `test_url`。

    :param protocol: PROXY Protocol
    :param host: PROXY Host
    :param port: PROXY Port
    :param timeout: Timeout Seconds
    :param username: Username for Authentication (default: None)
    :param password: Password for Authentication (default: None)
    :return: Nonnegative integer (成功，延遲 ms) 或 -1 (失敗)
    """
    if username is None or password is None:
        proxy_url = f"{protocol}://{host}:{port}"
    else:
        proxy_url = f"{protocol}://{username}:{password}@{host}:{port}"

    # 設定 requests 的 proxies 參數
    proxies = {"http": proxy_url, "https": proxy_url}

    try:
        # 發送請求測試
        response = requests.get(test_url, proxies=proxies, timeout=timeout)

        response.raise_for_status()
        return int(response.elapsed.total_seconds() * 1000)
    except Exception as e:
        log_error(f"test_proxy Error: {e}")
        
    return -1
