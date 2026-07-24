from src.updater import ProxyChecker, ProxyUpdater


if __name__ == "__main__":
    checker = ProxyChecker()
    updater = ProxyUpdater(checker)
    print(">> Updater is online <<")
    updater.run()
