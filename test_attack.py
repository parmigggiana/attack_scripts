import json

from pwn import log

with open("config.json", "r") as f:  # relative to CWD
    config: dict = json.load(f)


def local_test(exploit):
    def wrapper(*args, **kwargs):
        flags = exploit("127.0.0.1")
        log.info(f"We caught {flags = }")

    return wrapper


def nop_test(exploit):
    def wrapper(*args, **kwargs):
        nopteam = config["baseip"].format(id=0)

        flags = exploit(nopteam)
        result = submit_flags(flags)
        # TODO: add logic to check if everything is working with nopteam

    return wrapper


def self_test(exploit):
    def wrapper(*args, **kwargs):
        teamip = config["baseip"].format(id=config["team_id"])

        flags = exploit(teamip)
        log.info(f"We caught {flags = }")

    return wrapper


@local_test
def exploit(target_ip):
    log.info(f"{__name__} against {target_ip}!")


if __name__ == "__main__":
    exploit()
