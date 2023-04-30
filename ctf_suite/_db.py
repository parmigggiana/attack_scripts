import random
import pymongo
import uuid

import requests
from common import submit_flags, log

db_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = db_client["ctf"]
collection = db["flags"]


def save_flags(flags: list[str]):
    d = [{"_id": flag, "status": "unknown"} for flag in flags]

    res = collection.insert_many(d, ordered=False)

    return res


def submit_new_flags():  # I want this to run every 5 seconds or so
    flags = [x["_id"] for x in collection.find({"status": "unknown"}, ["_id"])]
    log.info("Submitting new flags...")
    try:
        ret = submit_flags(flags)
        # TODO: Parse response and update status
        for response in ret:
            f = response["flag"]
            status = response["status"]

            collection.update_one({"_id": f}, {"$set": {"status": status}})
    except requests.exceptions.ConnectTimeout:
        log.critical("Couldn't submit new flags.")


def main():
    flags = []
    for _ in range(random.randint(1, 5)):
        flags.append(uuid.uuid4().hex)
    print(flags)
    save_flags(flags)
    for x in collection.find():
        print(x)
    submit_new_flags()
    collection.delete_many({})


if __name__ == "__main__":
    main()
