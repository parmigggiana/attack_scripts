import time
from .common import  log, submit_flags, nopteam, teamip, queue

import config

def syncAttack(func):
    def wrapper(*args, **kwargs):
        while True:
            #log.critical(f"{func}: waiting for gametick")
            queue.get()
            start = time.time()
            func(*args, **kwargs)
            queue.task_done()
            elapsed = time.time() - start
            if elapsed > config.max_time:
                log.warn(f"{func.__name__} took more than {config.max_time} seconds")
            #log.critical(f"{func}: waiting = {barrier.n_waiting}")
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
