from queue import Empty, Full
import time
import importlib
import multiprocessing as mp
import ctf_suite as cs
from threading import Thread
import os
import watchdog.observers
import watchdog.events

from ctf_suite import log

stopSignal = 0


def worker(func):
    def wrapper(*args, **kwargs):
        log.info(f"Started {mp.current_process().name} (PID = {os.getpid()})")
        ret = func(*args, **kwargs)
        return ret

    return wrapper


@worker
def Attacker():
    while not stopSignal:
        tasks: list[Thread] = []
        # log.debug(f"{old_exploits = }, {old_highest_id = }")
        for i, exploit in enumerate(cs.exploits):
            log.info(f"Starting {exploit.__name__} ({i+1}/{cs.exploitsNumber})")
            for id in range(1, cs.config.highest_id + 1):
                target_ip = cs.config.baseip.format(id=id)
                t = Thread(
                    target=cs.syncAttack(exploit),
                    args=(target_ip,),
                    name=f"{exploit.__name__}_{target_ip}",
                )
                tasks.append(t)
                t.start()
        cs.configReloadQueue.get()
        cs.reloadEvent.set()
        log.info(
            "Exploits and/or highest_id have changed; respawning threads before next gametick"
        )
        for task in tasks:
            task.join()
        log.debug("[Attacker] Done reloading")
        cs.reloadEvent.clear()
        cs.configReloadQueue.task_done()
        importlib.reload(cs)

        log.debug("Attacker reloaded lib")
    else:
        for task in tasks:
            try:
                task.join()
            except:
                pass
        return 0


@worker
def GametickLoopManager():
    while not stopSignal:
        start = time.time()
        for i in range(cs.threadsNumber):
            cs.tokenQueue.put(i)
        cs.tokenQueue.join()
        elapsed = time.time() - start
        remaining = cs.config.tick_duration - elapsed
        if remaining < 0:
            log.warn(f"Took more than {cs.config.tick_duration:.2f} seconds!")
            continue
        l = log.progress(
            f"Took {elapsed:.2f} seconds. Waiting for {remaining:.2f} seconds"
        )
        try:
            s = time.time()
            cs.configReloadQueue.get(timeout=remaining * 0.99)
            cs.configReloadQueue.task_done()
            importlib.reload(cs)
            log.debug("GametickLoopManager reloaded lib")
            remaining -= time.time() - s
            time.sleep(remaining * 0.99)
        except Empty:
            pass
        l.success()

    else:
        return 0


@worker
def FlagSubmitter():
    while not stopSignal:
        try:
            s = time.time()
            cs.configReloadQueue.get(timeout=cs.config.flag_submission_delay)
            cs.configReloadQueue.task_done()
            importlib.reload(cs)
            log.debug("FlagSubmitter reloaded lib")
            remaining = cs.config.flag_submission_delay - (time.time() - s)
            if remaining > 0:
                time.sleep(remaining)
        except Empty:
            pass
        flags = cs.getNewFlags()
        if not flags:
            log.info("There is no new flags")
            continue
        log.info("Submitting new flags...")
        ret = cs.submit_flags(flags)
        cs.updateFlags(ret)
    else:
        return 0


class ExploitsModHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event: watchdog.events.FileSystemEvent):
        super().on_modified(event)
        if (
            event.event_type is watchdog.events.EVENT_TYPE_MODIFIED
            and event.is_directory
        ):
            log.info("Reloading exploits")
            # TODO: Signals to synchronize reloading on all processes


class ConfigModHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

        self.last_trigger = time.time()

    def on_modified(self, event: watchdog.events.FileSystemEvent):
        super().on_modified(event)
        if (
            (event.event_type is watchdog.events.EVENT_TYPE_MODIFIED)
            and (not event.is_directory)
            and ("config.py" in event.src_path)
            and ((time.time() - self.last_trigger) > 1)
        ):  # Added debouncing
            log.info("Reloading configs")
            for i in range(3):
                cs.configReloadQueue.put(i)

            cs.configReloadQueue.join()

        self.last_trigger = time.time()


@worker
def ChangesObserver():
    obs1 = watchdog.observers.Observer()
    obs2 = watchdog.observers.Observer()
    # print(obs1.__class__)
    event_handler1 = ExploitsModHandler()
    event_handler2 = ConfigModHandler()

    obs1.schedule(event_handler1, path="exploits", recursive=True)
    obs2.schedule(event_handler2, path="config.py")

    obs1.start()
    obs2.start()

    while True:
        time.sleep(2)

    obs1.stop()
    obs2.stop()
    obs1.join()
    obs2.join()


def main():
    # signal.signal(signal.SIGINT, signal_handler)
    log.info(f"Parent has PID = {os.getpid()}")
    pr = log.progress("Waiting for exploits to be loaded...")
    while not cs.exploits:  # keep refreshing until there's an exploit
        time.sleep(5)
        importlib.reload(cs)
    else:
        pr.success()
    processes = []

    processes.append(mp.Process(target=ChangesObserver, name="Changes Observer"))
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
