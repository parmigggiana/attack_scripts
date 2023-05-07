import os
import time
import signal

from concurrent.futures import ProcessPoolExecutor

from milkman.config import Config
from milkman.logger import logger
from milkman.exploits import Exploits
from milkman.processes import GametickManager, FileObserver, FlagSubmitter

conf = Config()


def stop_handler():
    print("SIGINT/SIGTERM received. Stopping app...")

    os.killpg(os.getpgid(0), signal.SIGINT)  # send SIGINT to process group


def main():
    # signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)
    log = logger.bind(file="app.log")
    log.info(f"Parent has PID = {os.getpid()}")
    log.info("Waiting for exploits to be loaded...")
    exploits = Exploits()

    while not exploits:  # keep refreshing until there's an exploit
        time.sleep(3)
    else:
        log.success("Done")

    executor = ProcessPoolExecutor(3)
    executor.submit(FileObserver)
    executor.submit(FlagSubmitter)
    executor.submit(GametickManager)

    executor.shutdown(
        wait=True, cancel_futures=False
    )  # waits for all tasks to finish first, so will hang
    return 0


if __name__ == "__main__":
    time.tzset()
    main()
