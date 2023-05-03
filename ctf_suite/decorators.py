import time
from .common import  log, submit_flags, nopteam, teamip, tokenQueue, reloadEvent

import config

def syncAttack(exploit):
    def wrapper(*args, **kwargs):
        while not reloadEvent.is_set():
            #log.critical(f"{func}: waiting for gametick")
            tokenQueue.get()
            if reloadEvent.is_set():
                break
            start = time.time()
            exploit(*args, **kwargs)
            tokenQueue.task_done()
            elapsed = time.time() - start
            if elapsed > config.max_time:
                log.warn(f"{exploit.__name__} took {elapsed:.2f} seconds")
        return
    return wrapper

def local_test(exploit):
    def wrapper(*args, **kwargs):
        flags = exploit("127.0.0.1")
        log.info(f"We caught {flags = }")

    return wrapper


def nop_test(exploit):
    def wrapper(*args, **kwargs):
        flags = exploit(nopteam)
        result = submit_flags(flags)
        # TODO: add logic to check if everything is working with nopteam

    return wrapper


def self_test(exploit):
    def wrapper(*args, **kwargs):
        flags = exploit(teamip)
        log.info(f"We caught {flags = }")

    return wrapper
