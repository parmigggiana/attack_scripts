import os
import time

from threading import Thread
from multiprocessing import JoinableQueue

import requests

from milkman.logger import logger
from milkman.config import Config
from milkman.exploits import Exploits, runExploit

"""
In earlier versions we were spawning n threads and handling synchronization in the thread level (instead of process level). That was more efficient as now we are allocating new threads for each gametick. While this may seem terrible practice, this removes the need for complex synchronization and solves the problems we had with reloading config or exploits on the fly. Does this make the code run slower? Technically, yes. However thread allocation is _really_ efficient; I ran a test spawning 10 millions threads and it took less than 0.3 seconds. Even if we run 100 exploits against 80 teams every gametick, the overhead from the thread allocation would be irrelevant (same test, with 100*80 threads took about 0.07 seconds).
"""


conf = Config()
exploits = Exploits()


def timeCounterThread(n, gametickQueue: JoinableQueue, threads: list[Thread]):
    log = logger.bind(file="gameloop.log")
    tick = conf["tick_duration"]
    for i in range(len(exploits) * conf["highest_id"]):
        gametickQueue.put(i)
    start = time.time()
    while gametickQueue._notempty:
        pass
    log.debug("All tokens given")
    gametickQueue.join()
    for t in threads:
        t.join()
    gametickQueue.close()
    elapsed = time.time() - start
    remaining = tick - elapsed
    if remaining < 0:
        log.warning(f"Tick {n} took more than {tick:.2f} seconds!")
    else:
        log.info(f"Took {elapsed:.2f} seconds. Waiting for {remaining:.2f} seconds")

    return


def waitStart():
    while True:  # Wait until the network is open
        url = "http://10.10.0.1/api/reports/status.json"
        try:
            status = requests.get(url)
            if status.json() != {"code": "UNKNOWN", "message": "An error has occurred"}:
                break
        except Exception:
            pass
        time.sleep(20)

    currentRound = status.json()["currentRound"]


def GametickManager():
    tick_n = 0
    log = logger.bind(file="gameloop.log")
    log.debug("GametickManager started")
    exploits = Exploits()

    waitStart()
    threads = []
    while True:
        tick_n += 1
        threads.clear()

        log.info(f"Starting gametick {tick_n}")
        gametickQueue = JoinableQueue()
        for i, exploit in enumerate(exploits):
            log.info(f"Starting {exploit.__module__} ({i+1}/{len(exploits)})")
            threads.append(runExploit(exploit, gametickQueue))

        Thread(
            target=timeCounterThread,
            args=(tick_n, gametickQueue, threads),
            name=f"tick_{tick_n}",
        ).start()

        time.sleep(conf["tick_duration"])
