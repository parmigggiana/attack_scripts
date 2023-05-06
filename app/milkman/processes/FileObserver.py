import time

from milkman.config import Config
from milkman.exploits import Exploits
from milkman.logger import logger
from watchdog.events import (
    FileModifiedEvent,
    FileSystemEvent,
    FileSystemEventHandler,
    EVENT_TYPE_MODIFIED,
)
from watchdog.observers import Observer


class ExploitsModHandler(FileSystemEventHandler):
    def on_modified(self, event: FileSystemEvent):
        super().on_modified(event)
        if event.event_type is FileModifiedEvent and event.is_directory:
            logger.info("Reloading exploits", extra={"file": "observer.log"})
            Exploits().load_exploits()


class ConfigModHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

        self.last_trigger = time.perf_counter()

    def on_modified(self, event: FileSystemEvent):
        super().on_modified(event)
        if (
            (event.event_type is EVENT_TYPE_MODIFIED)
            and (not event.is_directory)
            and ("config.py" in event.src_path)
            and ((time.perf_counter() - self.last_trigger) > 0.5)
        ):  # Added debouncing
            logger.info("Reloading configs", extra={"file": "observer.log"})
            Config().reload()

        self.last_trigger = time.perf_counter()


def FileObserver():
    log = logger.bind(file="observer.log")

    obs1 = Observer()
    obs2 = Observer()
    # print(obs1.__class__)
    event_handler1 = ExploitsModHandler()
    event_handler2 = ConfigModHandler()

    obs1.schedule(event_handler1, path="../exploits", recursive=True)
    obs2.schedule(event_handler2, path="../config.json")

    obs1.start()
    obs2.start()

    while True:
        time.sleep(10)

    obs1.stop()
    obs2.stop()
    obs1.join()
    obs2.join()
