import time
import requests

from milkman.config import Config
from milkman.logger import logger
from milkman.db import getNewFlags, updateFlags


def submit_flags(flags: list[str]):
    conf = Config()

    log = logger.bind(file="flagsubmitter.log")

    try:
        """
        this may be different for other CTFs (besides obviously the URL), so maybe it should be made into an editable module instead.
        """
        response = requests.put(
            "http://10.10.0.1:8080/flags",
            headers={"X-Team-Token": conf["TEAM_TOKEN"]},
            json=flags,
        )
        response = response.json()  # this is now a list
        log.info(f"Got {response = }")
        return response
    except requests.ConnectTimeout as e:
        log.critical("Gameserver didn't answer!")
        raise e

    except requests.JSONDecodeError as e:
        log.critical(f"JSON decoding error!\n{response = }")  # type: ignore
        raise e

    except Exception as e:
        log.critical(f"Unhandled exception was raised!\n{e}")


def FlagSubmitter():
    log = logger.bind(file="flagsubmitter.log")
    conf = Config()

    log.debug("FlagSubmitter started")
    while True:
        s = time.time()

        flags = getNewFlags()
        if not flags:
            # log.info("There is no new flags")
            time.sleep(5)
            continue

        log.info("Submitting new flags...")

        ret = submit_flags(flags)
        updateFlags(ret)

        remaining = conf["flag_submission_delay"] - (time.time() - s)
        if remaining > 0:
            time.sleep(remaining)
