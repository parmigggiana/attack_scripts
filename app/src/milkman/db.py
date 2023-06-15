import re
import time
import pymongo

from milkman.config import Config
from milkman.logger import logger

conf = Config()
_global_timer = time.time()

try:
    db_client = pymongo.MongoClient(conf["db_url"])
    db = db_client["ctf"]
    collection = db["flags"]
except Exception as e:
    logger.exception(
        "Can't connect to database; did you set it up properly?",
        extra={"file": "db.log"},
    )


def save_flags(flags: list[str], submitter: str):
    global _global_timer

    log = logger.bind(file="db.log")
    valid_flags = []

    if isinstance(flags, str):
        flags = [
            flags,
        ]
    for flag in flags:
        m = re.finditer(pattern=conf["flag_regex"], string=flag)
        if m:
            for f in m:
                valid_flags.append(f.group())

    if valid_flags:
        d = [
            {"_id": flag, "status": "Unknown", "submitter": submitter}
            for flag in valid_flags
        ]
        try:
            res = collection.insert_many(d, ordered=False)
            log.info(f"Storing valid flags from {submitter}: {valid_flags}")
            return res
        except pymongo.errors.BulkWriteError:  # type: ignore
            t = time.time()
            if t - _global_timer > 20:
                _global_timer = time.time()
                log.info(f"Duplicate flag(s) from exploit {submitter}")


def getNewFlags() -> list[str]:
    log = logger.bind(file="db.log")

    flags = [x["_id"] for x in collection.find({"status": "Unknown"}, ["_id"])]
    return flags


def updateFlags(ret):
    log = logger.bind(file="db.log")

    for response in ret:
        f = response["flag"]
        status = response["status"]

        collection.update_one({"_id": f}, {"$set": {"status": status}})
