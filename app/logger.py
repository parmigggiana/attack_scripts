import sys
from loguru import logger

conf = {
    "handlers": [
        {
            "sink": sys.stdout,
            "enqueue": True,
            "format": "{time:HH:mm:ss.SS} {name} [{level:^8}] : {message}",
            "level": "TRACE",
        },
        {
            "sink": "logs/db.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "logs/db.log",
            "level": "INFO",
        },
        {
            "sink": "logs/attacker.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "logs/attacker.log",
            "level": "INFO",
        },
        {
            "sink": "logs/backend.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "logs/backend.log",
            "level": "INFO",
        },
        {
            "sink": "logs/exploits.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "logs/exploits.log",
            "level": "DEBUG",
        },
        {
            "sink": "logs/observer.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "logs/observer.log",
            "level": "INFO",
        },
        {
            "sink": "logs/gameloop.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"] == "logs/gameloop.log",
            "level": "INFO",
        },
        {
            "sink": "logs/flagsubmitter.log",
            "format": "{time:HH:mm:ss.SS} [{level:^8}] : {message}",
            "enqueue": True,
            "filter": lambda record: record["extra"]["file"]
            == "logs/flagsubmitter.log",
            "level": "INFO",
        },
    ],
}

logger.configure(**conf)
exploits_logger = logger.bind(file="logs/exploits.log")
