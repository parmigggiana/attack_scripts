import sys

from loguru import logger

_logs_dir = "../logs"
_conf = {
    "handlers": [
        {
            "sink": sys.stdout,
            "enqueue": True,
            "format": "<d>{time:HH:mm:ss.SS}</d> <c>{name}</c> <level>[{level:^8}]</level> : {message}",
            "level": "WARNING",
            "colorize": True,
        },
        {
            "sink": f"{_logs_dir}/db.log",
            "format": "<d>{time:HH:mm:ss.SS}</d> | <level>{level:<8}</level>\t{message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "db.log",
            "level": "DEBUG",
            "colorize": True,
        },
        {
            "sink": f"{_logs_dir}/exploits.log",
            "format": "<d>{time:HH:mm:ss.SS}</d> | <level>{level:<8}</level>\t{message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "exploits.log",
            "level": "DEBUG",
            "colorize": True,
        },
        {
            "sink": f"{_logs_dir}/observer.log",
            "format": "<d>{time:HH:mm:ss.SS}</d> | <level>{level:<8}</level>\t{message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "observer.log",
            "level": "DEBUG",
            "colorize": True,
        },
        {
            "sink": f"{_logs_dir}/gameloop.log",
            "format": "<d>{time:HH:mm:ss.SS}</d> | <level>{level:<8}</level>\t{message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "gameloop.log",
            "level": "DEBUG",
            "colorize": True,
        },
        {
            "sink": f"{_logs_dir}/flagsubmitter.log",
            "format": "<d>{time:HH:mm:ss.SS}</d> | <level>{level:<8}</level>\t{message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "flagsubmitter.log",
            "level": "DEBUG",
            "colorize": True,
        },
    ],
}

logger.configure(**_conf)
logger = logger.bind(file="")
