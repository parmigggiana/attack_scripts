import json

from milkman.singleton import SingletonMeta


class Config(dict, metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.load_configs()

    def load_configs(self) -> None:
        with open("../config.json", "r") as f:  # relative to CWD
            x: dict = json.load(f)
            for key, value in x.items():
                self[key] = value


if __name__ == "__main__":  # for testing
    conf = Config()

    print(conf["highest_id"])
