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
    while gametickQueue._notempty:  # type: ignore
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
    """
    this may be different for other CTFs (besides obviously the URL), so maybe it should be made into an editable module instead.
    """
    while True:  # Wait until the network is open
        try:
            if isnetworkopen():
                break
        except Exception:
            pass
        time.sleep(20)


def GametickManager():
    tick_n = 0
    log = logger.bind(file="gameloop.log")
    log.debug("GametickManager started")

    if conf["wait_gamestart"]:
        waitStart()

    while True:
        if conf["use_timer"]:
            log.info(f"Starting gametick {tick_n}")
            start = time.time()
            rungametick(tick_n, log)
            time.sleep(conf["tick_duration"] - time.time() + start)
        else:
            waitGametickNotification(tick_n)
            log.info(f"Starting gametick {tick_n}")
            rungametick(tick_n, log)
        tick_n += 1


def rungametick(tick_n, log):
    threads = []
    gametickQueue = JoinableQueue()
    for i, exploit in enumerate(exploits):
        log.info(f"Starting {exploit.__module__} ({i+1}/{len(exploits)})")
        threads.append(runExploit(exploit, gametickQueue))

    Thread(
        target=timeCounterThread,
        args=(tick_n, gametickQueue, threads),
        name=f"tick_{tick_n}",
    ).start()


def waitGametickNotification(currentRound):
    url = "http://10.10.0.1/api/reports/status.json"
    status = requests.get(url)
    time.sleep(
        conf["tick_duration"] * 9 / 10
    )  # wait for most of the gametick; we don't want to harass the gameserver when it's obvious it won't be a new tick in a while
    while currentRound == status.json()["currentRound"]:
        time.sleep(
            conf["tick_duration"] / 20
        )  # keep asking with more frequency until it's time


def isnetworkopen():
    url = "http://10.10.0.1/api/reports/status.json"
    status = requests.get(url)
    if status.json() == {"code": "UNKNOWN", "message": "An error has occurred"}:
        return False
    else:
        return True
