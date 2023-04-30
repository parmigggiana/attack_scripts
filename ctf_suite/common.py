import re
import multiprocessing as mp
from threading import Thread
from typing import Iterable
from pwn import log
import json
import requests


class config:
    with open("config/config.json") as config_file:
        config = json.load(config_file)
        team_id = config["team_id"]
        highest_id = config["highest_id"]
        TEAM_TOKEN = config["TEAM_TOKEN"]
        max_time = config["max_time"]
        db_url = config["db_url"]
        flag_regex = re.compile(repr(config["flag_regex"]))
        baseip = config["baseip"]
        log_level = config["log_level"]
        tick_duration = config["tick_duration"]


def deploy_attack(exploit):
    def wrapper(*args, **kwargs):
        exit_code = 0
        tasks: list[Thread] = []
        for id in range(1, config.highest_id + 1):
            target_ip = config.baseip.format(id=id)
            tasks.append(Thread(target=exploit, args=(target_ip,), name=target_ip))
        for task in tasks:
            task.start()
        for task in tasks:
            task.join(timeout=config.max_time)
            if task.is_alive():
                exit_code = 1
                log.warning(
                    f"The {exploit} attack to {task.name} took more than {config.max_time} seconds!"
                )

        return exit_code

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


nopteam = config.baseip.format(id=0)
iplist = [
    config.baseip.format(id=id)
    for id in range(config.highest_id + 1)
    if id != config.team_id
]


def submit_flags(flags: str | Iterable):
    if flags is not list:
        flags = list(flags)

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


def save_flag():
    pass
    # Save the flag to a database (even a json might be good)
    # every few seconds another process will send all new flags to the
    # gameserver and classify them accordingly
