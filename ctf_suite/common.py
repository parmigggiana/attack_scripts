from concurrent.futures import thread
from genericpath import exists
import importlib
from typing import Iterable
from pwn import log
import requests
import config
from multiprocessing import JoinableQueue

from ._exploits import exploitsNumber

queue = JoinableQueue()

teamip = config.baseip.format(id=config.team_id)
nopteam = config.baseip.format(id=0)
iplist = [  # except nopteam and teamip
    config.baseip.format(id=id)
    for id in range(1, config.highest_id + 1)
    if id != config.team_id
]

threadsNumber = len(iplist) * exploitsNumber


def submit_flags(flags: str | Iterable):
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

        return response
    except requests.ConnectTimeout as e:
        log.critical("Gameserver is unreachable!")
        raise e

    except requests.JSONDecodeError as e:
        log.critical(f"JSON decoding error!\n{response = }")
        raise e
