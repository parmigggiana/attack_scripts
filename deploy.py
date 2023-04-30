import time
import importlib
from pwn import log
import json
from multiprocessing import Process
import ctf_suite


def main():
    with open("config/config.json") as config_file:
        config = json.load(config_file)
        log_level = config["log_level"]
        tick_duration = config["tick_duration"]

    log.setLevel(log_level)  # debug, info, warning, error

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
        remaining = (tick_duration - elapsed) * 0.99
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
