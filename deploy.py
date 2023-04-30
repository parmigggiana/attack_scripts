import time
import importlib
from pwn import log
import json
from multiprocessing import Process
import ctf_suite
from ctf_suite import config


def main():
    log.setLevel(config.log_level)  # debug, info, warning, error
    while not ctf_suite.exploits:  # keep refreshing until there's an exploit
        importlib.reload(ctf_suite)
        time.sleep(5)

    while True:
        start = time.time()
        processes: list[Process] = []
        for exploit in ctf_suite.exploits:
            p = Process(target=ctf_suite.deploy_attack(exploit), name=exploit.__name__)
            processes.append(p)
            log.info(f"Creating {p.name} process...")
        for p in processes:
            p.start()
        for p in processes:
            p.join()
            if p.exitcode != 0:
                log.warn(f"Process {p.name} ended with status: {p.exitcode}")
            else:
                log.info(f"Process {p.name} ended successfully")
            p.terminate()
        end = time.time()
        elapsed = end - start
        remaining = (config.tick_duration - elapsed) * 0.99
        if remaining < 0:
            log.warn(f"Our exploits took {elapsed:.2f} seconds!")
            continue
        log.info(
            f"Our exploit took {elapsed:.2f} seconds, waiting for {remaining:.2f} before running again..."
        )
        time.sleep(remaining)
        importlib.reload(ctf_suite)


if __name__ == "__main__":
    main()
