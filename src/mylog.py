import logging

from src.settings import *

# Configure logging to a file
logging.basicConfig(
    filename=DIARY_LOG_PATH,    # Name of the file where logs will be stored
    filemode='a',               # 'a' to append logs, 'w' to overwrite the file on each run
    level=logging.INFO,         # Capture INFO, WARNING, ERROR, and CRITICAL logs
    format='%(asctime)s - %(levelname)s - %(message)s', # Log line format
    datefmt='%Y-%m-%d %H:%M:%S',# Date-time format
    encoding="utf-8"
)

def log_info(info: str, *args, **kwargs):
    logging.info(info, *args, **kwargs)

def log_warning(warning: str, *args, **kwargs):
    logging.warning(warning, *args, **kwargs)

def log_error(error: str, *args, **kwargs):
    logging.warning(error, *args, **kwargs)
