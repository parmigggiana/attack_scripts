import sys
import time
import signal
import requests

from milkman.config import Config
from milkman.logger import logger
from milkman.db import getNewFlags, updateFlags


def sigint_handler():
    print("stopping flagsubmitter")
    sys.exit(0)


def submit_flags(flags: str | list[str]):
    conf = Config()

    log = logger.bind(file="flagsubmitter.log")

    try:
        response = requests.put(
            "http://10.10.0.1:8080/flags",
            headers={"X-Team-Token": conf["TEAM_TOKEN"]},
            json=flags,
            timeout=5,
        )
        response = response.json()["Flags"]  # this is now a list
        log.info(f"Got {response = }")
        return response
    except requests.ConnectTimeout as e:
        log.critical("Gameserver is unreachable!")
        raise e

    except requests.JSONDecodeError as e:
        log.critical(f"JSON decoding error!\n{response = }")
        raise e


def FlagSubmitter():
    signal.signal(signal.SIGINT, sigint_handler)
    log = logger.bind(file="flagsubmitter.log")
    conf = Config()

    while True:
        s = time.perf_counter()

        flags = getNewFlags()
        if flags:
            log.info("Submitting new flags...")
            ret = submit_flags(flags)
            updateFlags(ret)
        else:
            log.info("There is no new flags")

        remaining = conf["flag_submission_delay"] - (time.perf_counter() - s)
        if remaining > 0:
            time.sleep(remaining)
