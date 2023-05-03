import logging
import time
import importlib
from pwn import log
import multiprocessing as mp
import ctf_suite as cs
from threading import Thread
import os

stopSignal = 0


""" def signal_handler(signal, frame):
    print("called signal handler")
    stopSignal = 1
    cs.gametickEvent.set()
    cs.barrier.abort()
    raise KeyboardInterrupt
 """


def Attacker():
    log.info(f"Started Attacker (PID = {os.getpid()})")
    while not stopSignal:
        tasks: list[Thread] = []
        old_exploits = cs.exploits
        old_highest_id = cs.config.highest_id
        log.debug(f"{old_exploits = }, {old_highest_id = }")
        for i, exploit in enumerate(old_exploits):
            log.info(f"Starting {exploit.__name__} ({i+1}/{cs.exploitsNumber})")
            for id in range(1, old_highest_id + 1):
                target_ip = cs.config.baseip.format(id=id)
                t = Thread(
                    target=cs.syncAttack(exploit),
                    args=(target_ip,),
                    name=f"{exploit.__name__}_{target_ip}",
                )
                tasks.append(t)
                t.start()
        while True:
            # log.debug("Waiting for next gametick")
            importlib.reload(cs)
            if old_exploits != cs.exploits and old_highest_id != cs.config.highest_id:
                break
        log.info(
            "Exploits and/or highest_id have changed since last gametick; respawning threads"
        )
        for task in tasks:
            task.join()
    else:
        for task in tasks:
            try:
                task.join()
            except:
                pass
        return 0


def GametickLoopManager():
    log.info(f"Started Gametick Loop Manager (PID = {os.getpid()})")
    while not stopSignal:
        importlib.reload(cs)
        start = time.time()
        for i in range(cs.threadsNumber):
            cs.queue.put(i)
        cs.queue.join()
        elapsed = time.time() - start
        remaining = cs.config.tick_duration - elapsed
        if remaining < 0:
            log.warn(f"Took more than {cs.config.tick_duration:.2f} seconds!")
            continue
        l = log.progress(
            f"Took {elapsed:.2f} seconds. Waiting for {remaining:.2f} seconds"
        )
        time.sleep(remaining * 0.99)
        l.success()

    else:
        return 0


def FlagSubmitter():
    log.info(f"Started Flag Submitter (PID = {os.getpid()})")
    while not stopSignal:
        importlib.reload(cs)
        time.sleep(cs.config.flag_submission_delay)
        flags = cs.getNewFlags()
        if not flags:
            log.info("There is no new flags")
            continue
        log.info("Submitting new flags...")
        ret = cs.submit_flags(flags)
        cs.updateFlags(ret)
    else:
        return 0


def main():
    log.setLevel(cs.config.log_level)  # debug, info, warning, error

    # signal.signal(signal.SIGINT, signal_handler)
    log.info(f"Parent has PID = {os.getpid()}")
    pr = log.progress("Waiting for exploits to be loaded...")
    while not cs.exploits:  # keep refreshing until there's an exploit
        time.sleep(5)
        importlib.reload(cs)
    else:
        pr.success()
    processes = []

    processes.append(mp.Process(target=Attacker, name="Attacks Manager"))
    processes.append(
        mp.Process(target=GametickLoopManager, name="Gametick Loop Manager")
    )
    processes.append(mp.Process(target=FlagSubmitter, name="Flags Submitter"))

    for p in processes:
        p.start()
    for p in processes:
        p.join()
        if p.exitcode != 0:
            log.warn(f"Process {p.name} ended with status: {p.exitcode}")
        else:
            log.info(f"Process {p.name} ended successfully")
        p.terminate()
    return 0


if __name__ == "__main__":
    main()
