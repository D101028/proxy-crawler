
#### Crawler Settings ###
#########################
DEFAULT_HEADERS         = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}   # 預設 HEADER for Crawlers
DEFAULT_TIMEOUT         = 10                        # 預設超時秒數
DEFAULT_MAX_RETRY       = 3                         # 預設最大重試次數

##### Proxy Testing #####
#########################
TEST_URL                = "https://www.google.com"  # Proxy 節點代理訪問測試用網址
PING_TIMEOUT_MS         = 5000                      # Proxy Host ping 延遲 timeout
RESPONSE_TIMEOUT_MS     = 8000                      # Proxy 節點代理延遲 timeout 毫秒數


##### Proxy Updater #####
#########################
MAX_WORKERS             = 50                        # 最大同時測試節點數
CHECK_INTERVAL          = 30                        # 檢查週期分鐘數
OUTPUT_JSON_PATH        = "./proxies.json"          # 輸出節點文件位置


### Logging Settings ####
#########################
DIARY_LOG_PATH          = "./log/diary.log"         # 日誌檔案位置

