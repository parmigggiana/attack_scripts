from typing import Iterable
import requests
import config
from multiprocessing import Event, JoinableQueue
from logger import logger

tokenQueue = JoinableQueue()
reloadEvent = Event()

teamip = config.baseip.format(id=config.team_id)
nopteam = config.baseip.format(id=0)


def submit_flags(flags: str | Iterable):
    log = logger.bind(file="flagsubmitter.log")
    if flags is not list:
        flags = list(flags)

    assert flags
    assert isinstance(flags, list)
    assert isinstance(flags[0], str)
    response = requests.Response()

    try:
        response = requests.put(
            "http://10.10.0.1:8080/flags",
            headers={"X-Team-Token": config.TEAM_TOKEN},
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