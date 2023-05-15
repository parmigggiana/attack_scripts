import re
import uuid
import random
import pymongo

from milkman.config import Config
from milkman.logger import logger

conf = Config()
try:
    db_client = pymongo.MongoClient(conf["db_url"])
    db = db_client["ctf"]
    collection = db["flags"]
except Exception as e:
    logger.exception(
        "Can't connect to database; did you set it up properly?",
        extra={"file": "db.log"},
    )


def save_flags(flags: list[str]):
    log = logger.bind(file="db.log")
    valid_flags = []

    if isinstance(flags, str):
        flags = [flags]

    for flag in flags:
        if re.match(pattern=conf["flag_regex"], string=flag):
            valid_flags.append(flag)
        else:
            log.warning(f"Received flag that doesn't match regex: {flag}")

    if valid_flags:
        d = [{"_id": flag, "status": "unknown"} for flag in valid_flags]
        log.info(f"Storing valid flags: {valid_flags}")
        res = collection.insert_many(d, ordered=False)
        return res


def getNewFlags() -> list[str]:
    log = logger.bind(file="db.log")

    flags = [x["_id"] for x in collection.find({"status": "unknown"}, ["_id"])]
    return flags


def updateFlags(ret):
    log = logger.bind(file="db.log")

    # TODO: Parse response and update status
    for response in ret:
        f = response["flag"]
        status = response["status"]

        collection.update_one({"_id": f}, {"$set": {"status": status}})


def main():  # Just for testing purposes
    flags = []
    for _ in range(random.randint(1, 5)):
        flags.append(uuid.uuid4().hex)
    print(flags)
    save_flags(flags)
    for x in collection.find():
        print(x)
    # submit_new_flags()
    collection.delete_many({})


if __name__ == "__main__":
    main()
