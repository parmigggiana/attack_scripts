import sys

from loguru import logger

_logs_dir = "../logs"
_conf = {
    "handlers": [
        {
            "sink": sys.stdout,
            "enqueue": True,
            "format": "{time:HH:mm:ss.SS} {name} [{level:^8}] : {message}",
            "level": "TRACE",
        },
        {
            "sink": f"{_logs_dir}/db.log",
            "format": "{time:HH:mm:ss.SS} | {level:^8} | : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "db.log",
            "level": "DEBUG",
        },
        {
            "sink": f"{_logs_dir}/exploits.log",
            "format": "{time:HH:mm:ss.SS} | {level:^8} | : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "exploits.log",
            "level": "DEBUG",
        },
        {
            "sink": f"{_logs_dir}/observer.log",
            "format": "{time:HH:mm:ss.SS} | {level:^8} | : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "observer.log",
            "level": "DEBUG",
        },
        {
            "sink": f"{_logs_dir}/gameloop.log",
            "format": "{time:HH:mm:ss.SS} | {level:^8} | : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "gameloop.log",
            "level": "DEBUG",
        },
        {
            "sink": f"{_logs_dir}/flagsubmitter.log",
            "format": "{time:HH:mm:ss.SS} | {level:^8} | : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "flagsubmitter.log",
            "level": "DEBUG",
        },
    ],
}

logger.configure(**_conf)
logger = logger.bind(file="")
