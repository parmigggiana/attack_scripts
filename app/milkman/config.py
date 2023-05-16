from json import load
from jsonschema import validate

from milkman.logger import logger
from milkman.singleton import SingletonMeta


class Config(dict, metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.schema = {
            "type": "object",
            "properties": {
                "team_id": {"type": "integer"},
                "highest_id": {"type": "integer"},
                "TEAM_TOKEN": {"type": "string"},
                "max_thread_time": {"type": "number"},
                "tick_duration": {"type": "number"},
                "flag_regex": {"type": "string"},
                "baseip": {"type": "string"},
                "db_url": {"type": "string"},
                "flag_submission_delay": {"type": "number"},
            },
        }
        self.load_configs()

    def load_configs(self) -> None:
        with open("../configs/config.json", "r") as f:  # relative to CWD
            x: dict = load(f)
            try:
                validate(x, self.schema)
                for key, value in x.items():
                    self[key] = value
            except Exception:
                logger.exception(f"Invalid config")
                return


if __name__ == "__main__":  # for testing
    conf = Config()

    print(conf["highest_id"])
