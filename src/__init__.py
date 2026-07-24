import os

from src.settings import *

def init_data() -> None:
    # Create log files
    if not os.path.isdir(os.path.dirname(DIARY_LOG_PATH)):
        os.mkdir(os.path.dirname(DIARY_LOG_PATH))
    if not os.path.isfile(DIARY_LOG_PATH):
        with open(DIARY_LOG_PATH, "w") as fp:
            fp.write("")

    # Create proxy files
    if not os.path.isdir(os.path.dirname(OUTPUT_JSON_PATH)):
        os.mkdir(os.path.dirname(OUTPUT_JSON_PATH))
    if not os.path.isfile(OUTPUT_JSON_PATH):
        with open(OUTPUT_JSON_PATH, "w") as fp:
            fp.write("[]")

init_data()
