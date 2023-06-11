import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from milkman.config import Config
from milkman.exploits import Exploits
from milkman.logger import logger

observers = []
log = logger.bind(file="observer.log")


class ExploitsModHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

        self.last_trigger = time.time()

    def on_modified(self, event):
        if (time.time() - self.last_trigger) > 1:
            self.last_trigger = time.time()
            log.info("Reloading exploits", extra={"file": "observer.log"})
            Exploits().load_exploits()


class ConfigModHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

        self.last_trigger = time.time()

    def on_modified(self, event):
        trigger = time.time()
        if (trigger - self.last_trigger) > 0.5:  # Added debouncing
            log.info("Reloading configs", extra={"file": "observer.log"})
            Config().load_configs()
            self.last_trigger = time.time()


def FileObserver():
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
