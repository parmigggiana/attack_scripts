import re
import time

from pymongo import MongoClient

from milkman.config import Config
from milkman.logger import logger

conf = Config()
_global_timer = time.time()
log = logger.bind(file="db.log")

try:
    db_client = MongoClient(conf["db_url"])
    db = db_client["ctf"]
    collection = db["flags"]
except Exception as e:
    log.exception("Can't connect to database; did you set it up properly?")


def save_flags(flags: list[str | bytes] | str | bytes, submitter: str):
    global _global_timer

    log = logger.bind(file="db.log")
    valid_flags = []

    if isinstance(flags, str) or isinstance(flags, bytes):
        flags = [
            flags,
        ]
    for flag in flags:
        if isinstance(flag, bytes):
            try:
                flag = flag.decode("utf-8")
            except Exception as e:
                log.warning(f"Error while decoding flag from {submitter}")
                log.warning(f"returned value: {flag}")
                log.debug(f"{e}")

        m = re.finditer(pattern=conf["flag_regex"], string=flag)
        if m:
            for f in m:
                valid_flags.append(f.group())

    if valid_flags:
        d = [
            {
                "_id": flag,
                "status": "Unknown",
                "submitter": submitter,
                "saved_timestamp": time.time(),
                "response_timestamp": 0,
                "reason": "",
            }
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
    flags = [x["_id"] for x in collection.find({"status": "Unknown"}, ["_id"])]
    return flags


def updateFlags(ret):
    for response in ret:
        f = response["flag"]
        status = response["status"]
        msg = response["msg"]
        reason = "".join(msg.split(" ")[2:]) if not status else ""
        collection.update_one(
            {"_id": f},
            {
                "$set": {
                    "status": status,
                    "reason": reason,
                    "response_timestamp": time.time(),
                }
            },
        )
