import sys
from loguru import logger
from pathlib import Path

logs_dir = "logs"
conf = {
    "handlers": [
        {
            "sink": sys.stdout,
            "enqueue": True,
            "format": "{time:HH:mm:ss.SS} {name} [{level:^8}] : {message}",
            "level": "TRACE",
        },
        {
            "sink": f"{logs_dir}/db.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "db.log",
            "level": "INFO",
        },
        {
            "sink": f"{logs_dir}/attacker.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "attacker.log",
            "level": "INFO",
        },
        {
            "sink": f"{logs_dir}/exploits.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "exploits.log",
            "level": "DEBUG",
        },
        {
            "sink": f"{logs_dir}/observer.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "observer.log",
            "level": "INFO",
        },
        {
            "sink": f"{logs_dir}/gameloop.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "gameloop.log",
            "level": "INFO",
        },
        {
            "sink": f"{logs_dir}/flagsubmitter.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "flagsubmitter.log",
            "level": "INFO",
        },
    ],
}

logger.configure(**conf)
exploits_logger = logger.bind(file="exploits.log")
