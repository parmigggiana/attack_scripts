import sys
import time
import signal

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from milkman.config import Config
from milkman.exploits import Exploits
from milkman.logger import logger

observers = []


def sigint_handler():
    print("stopping observer")
    for obs in observers:
        obs.stop()
        obs.join()
    sys.exit(0)


class ExploitsModHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

        self.last_trigger = time.perf_counter()

    def on_modified(self, event):
        if (time.perf_counter() - self.last_trigger) > 1:
            logger.info("Reloading exploits", extra={"file": "observer.log"})
            Exploits().load_exploits()
            self.last_trigger = time.perf_counter()


class ConfigModHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

        self.last_trigger = time.perf_counter()

    def on_modified(self, event):
        trigger = time.perf_counter()
        if (trigger - self.last_trigger) > 0.5:  # Added debouncing
            logger.info("Reloading configs", extra={"file": "observer.log"})
            Config().load_configs()
            self.last_trigger = time.perf_counter()


def FileObserver():
    signal.signal(signal.SIGINT, sigint_handler)

    log = logger.bind(file="observer.log")

    exploitsObserver = Observer()
    configObserver = Observer()
    exploitsHandler = ExploitsModHandler()
    configHandler = ConfigModHandler()

    exploitsObserver.schedule(exploitsHandler, path="../exploits", recursive=True)
    configObserver.schedule(configHandler, path="../config.json")

    exploitsObserver.start()
    configObserver.start()

    global observers
    observers.append(exploitsObserver)
    observers.append(configObserver)

    log.debug("Observer started")
    while True:
        time.sleep(2)
