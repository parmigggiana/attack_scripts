import sys
from loguru import logger

conf = {
    "handlers": [
        {
            "sink": sys.stdout,
            "enqueue": True,
            "format": "{time} {name} [{level:^8}] : {message}",
        },
        {
            "format": "{time} [{level:^8}] : {message}",
            "enqueue": True,
        },
    ],
}

logger.configure(**conf)
