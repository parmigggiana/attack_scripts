import random
import pymongo
import uuid
import config
from .common import logger

log = logger.bind(file="db.log")
try:
    db_client = pymongo.MongoClient(config.db_url)
    db = db_client["ctf"]
    collection = db["flags"]
except Exception as e:
    log.exception("Can't connect to database; did you set it up properly?")


def save_flags(flags: list[str]):
    d = [{"_id": flag, "status": "unknown"} for flag in flags]

    res = collection.insert_many(d, ordered=False)

    return res


def getNewFlags() -> list[str]:
    flags = [x["_id"] for x in collection.find({"status": "unknown"}, ["_id"])]
    return flags


def updateFlags(ret):
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
