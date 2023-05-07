import os
import sys
import time
import signal

from threading import Thread
from multiprocessing import JoinableQueue

from milkman.config import Config
from milkman.exploits import Exploits
from milkman.logger import logger

"""
In earlier versions we were spawning n threads and handling synchronization in the thread level (instead of process level). That was more efficient as now we are allocating new threads for each gametick. While this may seem terrible practice, this removes the need for complex synchronization and solves the problems we had with reloading config or exploits on the fly. Does this make the code run slower? Technically, yes. However thread allocation is _really_ efficient; I ran a test spawning 10 millions threads and it took less than 0.3 seconds. Even if we run 100 exploits against 80 teams every gametick, the overhead from the thread allocation would be irrelevant (same test, with 100*80 threads took about 0.07 seconds).
"""


conf = Config()


def sigint_handler():
    print("stopping gametick")
    os.killpg(os.getpgid(0), signal.SIGINT)
    sys.exit(0)


def timeCounterThread(n, gametickQueue: JoinableQueue):
    log = logger.bind(file="gameloop.log")
    tick = conf["tick_duration"]

    for i in range(len(Exploits()) * conf["highest_id"]):
        gametickQueue.put(i)
    start = time.perf_counter()
    while gametickQueue._notempty:
        pass
    gametickQueue.join()
    elapsed = time.perf_counter() - start
    remaining = tick - elapsed
    if remaining < 0:
        log.warning(f"Tick {n} took more than {tick:.2f} seconds!")
    else:
        log.info(f"Took {elapsed:.2f} seconds. Waiting for {remaining:.2f} seconds")

    return


def launchAttack(exploit, target_ip: str, gametickQueue):
    log = logger.bind(file=f"exploits.log")
    level = "INFO"

    gametickQueue.get()
    start = time.perf_counter()
    exploit(target_ip)
    elapsed = time.perf_counter() - start
    gametickQueue.task_done()

    if elapsed > conf["max_thread_time"]:
        level = "WARNING"
    log.log(level, f"{exploit.__name__} took {elapsed:.2f} seconds")
    return


def GametickManager():
    signal.signal(signal.SIGINT, sigint_handler)

    tick_n = 0
    log = logger.bind(file="gameloop.log")
    exploits = Exploits()

    while True:
        tick_n += 1
        log.info(f"Starting gametick {tick_n}")
        gametickQueue = JoinableQueue()
        Thread(
            target=timeCounterThread,
            args=(tick_n, gametickQueue),
            name=f"tick_{tick_n}",
        ).start()
        for i, exploit in enumerate(exploits):
            log.info(f"Starting {exploit.__name__} ({i+1}/{len(exploits)})")
            for id in range(1, conf["highest_id"] + 1):
                if id == conf["team_id"]:
                    continue
                target_ip = conf["baseip"].format(id=id)
                t = Thread(
                    target=launchAttack,
                    args=(
                        exploit,
                        target_ip,
                        gametickQueue,
                    ),
                    name=f"{exploit.__name__}_{target_ip}",
                )
                t.start()

        time.sleep(conf["tick_duration"])
