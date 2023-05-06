from milkman.config import Config
from milkman.logger import logger
from milkman.processes.FlagSubmitter import submit_flags

conf = Config()


def local_test(exploit):
    def wrapper(*args, **kwargs):
        flags = exploit("127.0.0.1")
        logger.info(f"We caught {flags = }")

    return wrapper


def nop_test(exploit):
    def wrapper(*args, **kwargs):
        nopteam = Config()["baseip"].format(id=0)

        flags = exploit(nopteam)
        result = submit_flags(flags)
        # TODO: add logic to check if everything is working with nopteam

    return wrapper


def self_test(exploit):
    def wrapper(*args, **kwargs):
        teamip = Config()["baseip"].format(id=Config()["team_id"])

        flags = exploit(teamip)
        logger.info(f"We caught {flags = }")

    return wrapper
