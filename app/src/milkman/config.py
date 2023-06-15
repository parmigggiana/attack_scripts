from json import load
from typing import Any
from jsonschema import ValidationError, validate

from milkman.logger import logger
from morel.singleton import SingletonMeta
from morel import Targets

Targets().setBaseDir("../targets")


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
                "status_check_delay": {"type": "number"},
                "wait_gamestart": {"type": "boolean"},
                "ping_before_exploit": {"type": "boolean"},
                "use_timer": {"type": "boolean"},
                "check_status": {"type": "boolean"},
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
            except ValidationError:
                logger.exception(f"Invalid config")
                return

    def __getitem__(self, __key: Any) -> Any:
        return super().__getitem__(__key)


if __name__ == "__main__":  # for testing
    conf = Config()

    print(conf["highest_id"])
