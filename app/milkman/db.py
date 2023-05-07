import uuid
import random
import pymongo

from milkman.config import Config
from milkman.logger import logger

try:
    db_client = pymongo.MongoClient(Config()["db_url"])
    db = db_client["ctf"]
    collection = db["flags"]
except Exception as e:
    logger.exception(
        "Can't connect to database; did you set it up properly?",
        extra={"file": "db.log"},
    )


def save_flags(flags: list[str]):
    log = logger.bind(file="db.log")

    d = [{"_id": flag, "status": "unknown"} for flag in flags]

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
