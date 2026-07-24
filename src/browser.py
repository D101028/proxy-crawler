import requests
from bs4 import BeautifulSoup
from requests import Response

from urllib.parse import urlparse, urlunparse

class ExceedMaxRetryError(Exception):
    """當嘗試次數超出範圍拋出"""
    pass

class Browser:
    def __init__(self, base_url: str | None = None, headers: dict | None = None, cookies: dict | None = None, 
                 timeout: int = 10, max_retry: int = 3):
        """
        Initializes the crawler instance with default settings.

        Attributes:
            cookies (dict or None): 用於儲存請求時的 cookies，格式應為 {'cookie_name': 'cookie_value', ...}。
            headers (dict): HTTP 請求標頭。
            base_url (str): 目標網站的基礎 URL。
            session (requests.Session): requests 的 session 物件，用於維持連線狀態。
            timeout (int): 請求逾時時間（秒）。
            max_retry (int): 請求失敗時的重試次數。
            last_response (requests.Response or None): 上一次的 HTTP 回應。
        """
        if headers is None:
            headers = {}
        self.cookies: dict | None = cookies                 # 用於儲存請求時的 cookies
        self.headers: dict = headers                        # HTTP 請求標頭
        self.base_url: str | None = base_url                # 目標網站的基礎 URL
        self.session: requests.Session = requests.Session() # requests 的 session 物件
        self.timeout: int = timeout                         # 請求逾時時間（秒）
        self.max_retry: int = max_retry                     # 請求失敗時的重試次數
        self.last_response: requests.Response | None = None # 上一次的 HTTP 回應

    def set_base_url(self, url: str):
        """設定目標網站的基礎 URL"""
        self.base_url = url

    def set_headers(self, headers: dict):
        """設定 HTTP 請求標頭"""
        self.headers = headers

    def set_cookies(self, cookies: dict):
        """設定 cookies"""
        self.cookies = cookies

    def request(self, method: str, url: str, **kwargs) -> Response:
        """發送 HTTP 請求，支援重試機制"""
        if not url.startswith("http"):
            if self.base_url is None:
                raise Exception(f"Invalid base_url: {self.base_url}")
            full_url = self.base_url + url
        else:
            full_url = url
        err = None
        for _ in range(self.max_retry):
            try:
                response = self.session.request(
                    method,
                    full_url,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout,
                    **kwargs
                )
                self.last_response = response
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                err = e
                continue
        else:
            if err is not None:
                raise err
            raise ExceedMaxRetryError(f"Exceed Max Retry: {self.max_retry}")

    def get(self, url: str | None = None, **kwargs) -> Response:
        """發送 GET 請求"""
        if url is None:
            if self.base_url is None:
                raise Exception(f"Invalid base_url: {self.base_url}")
            return self.request("GET", self.base_url, **kwargs)
        return self.request("GET", url, **kwargs)

    def post(self, url: str, data=None, json=None, **kwargs) -> Response:
        """發送 POST 請求"""
        return self.request("POST", url, data=data, json=json, **kwargs)

    def goto(self, url: str, method: str="GET", **kwargs) -> Response:
        """
        訪問指定 URL，並自動更新 base_url 為該 URL 的主機部分。
        預設使用 GET 方法，可指定其他 HTTP 方法。
        """
        response = self.request(method, url, **kwargs)
        if not isinstance(response, str):
            parsed = urlparse(response.url)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        return response


