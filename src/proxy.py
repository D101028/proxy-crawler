from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, TypedDict

from src.settings import *

class ProxyNodeDict(TypedDict):
    protocol: str
    host: str
    port: int
    username: str | None
    password: str | None
    
    anonymity: str | None
    code: str | None
    country: str | None

@dataclass(frozen=True) # 設定 frozen=True，確保屬性不可變且自動生成安全的 __hash__
class ProxyNode:
    # 唯一識別身分與連線資料（不可變）
    protocol: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    
    # 附加元資料（不參與等價評估，但同樣不可變）
    anonymity: str | None = None
    code: str | None = None
    country: str | None = None

    def __eq__(self, other: Any) -> bool:
        # 安全的型態檢查，防止與非同類物件比較時崩潰
        if not isinstance(other, ProxyNode):
            return NotImplemented
        return (
            self.protocol == other.protocol and
            self.host == other.host and
            self.port == other.port and
            self.username == other.username and
            self.password == other.password
        )

    def __hash__(self) -> int:
        # 使用 Tuple 進行雜湊，效能比字串拼接（get_url）更快、更安全
        return hash((self.protocol, self.host, self.port, self.username, self.password))

    def get_url(self) -> str:
        if self.username is None or self.password is None:
            return f"{self.protocol}://{self.host}:{self.port}"
        return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"

    def to_dict(self) -> ProxyNodeDict:
        return {
            "protocol": self.protocol, 
            "host": self.host, 
            "port": self.port, 
            "username": self.username, 
            "password": self.password, 
            "anonymity": self.anonymity, 
            "code": self.code, 
            "country": self.country
        }


class ProxyStatusDict(TypedDict):
    alive: bool | None
    latency_ms: int | None
    response_ms: int | None
    last_checked: str

# 測試結果類別
@dataclass(frozen=True)
class ProxyStatus:
    alive: bool | None = None
    latency_ms: int | None = None
    response_ms: int | None = None
    # 使用 default_factory 確保每次實例化都抓到當下的最新時間
    last_checked: datetime = field(default_factory=datetime.now)

    @classmethod
    def get_null_status(cls) -> 'ProxyStatus':
        return ProxyStatus(last_checked=datetime.min)  # 將初始時間設為最小值，代表「從未檢查」

    def to_dict(self) -> ProxyStatusDict:
        return {
            "alive": self.alive, 
            "latency_ms": self.latency_ms, 
            "response_ms": self.response_ms, 
            "last_checked": self.last_checked.strftime("%Y-%m-%d %H:%M:%S")
        }

