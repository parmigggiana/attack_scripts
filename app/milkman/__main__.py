import os
import time

import multiprocessing as mp

from milkman.config import Config
from milkman.logger import logger
from milkman.exploits import Exploits
from milkman.processes import GametickManager, FileObserver, FlagSubmitter

configReloadQueue = mp.JoinableQueue()
exploitsReloadEvent = mp.Event()
conf = Config()


def main():
    # signal.signal(signal.SIGINT, signal_handler)
    log = logger.bind(file="app.log")
    log.info(f"Parent has PID = {os.getpid()}")
    log.info("Waiting for exploits to be loaded...")
    exploits = Exploits()

    while not exploits:  # keep refreshing until there's an exploit
        time.sleep(5)
    else:
        log.success("Done")

    processes = []
    processes.append(mp.Process(target=FileObserver, name="Config/Exploits Observer"))

    processes.append(
        mp.Process(
            target=GametickManager,
            name="Gametick Manager",
        )
    )
    processes.append(mp.Process(target=FlagSubmitter, name="Flags Submitter"))

    for p in processes:
        p.start()
    for p in processes:
        p.join()
        if p.exitcode != 0:
            log.warning(f"Process {p.name} ended with status: {p.exitcode}")
        else:
            log.info(f"Process {p.name} ended successfully")
        p.terminate()
    return 0


if __name__ == "__main__":
    main()
