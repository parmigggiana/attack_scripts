import time
import json
import requests


with open("../configs/config.json", "r") as f:  # relative to CWD
    conf: dict = json.load(f)


def scrape_status(logger=None):
    """
    Returns a dictionary
    {
        'WAQS': {'CHECK_SLA':101, 'GET_FLAG': 101, 'PUT_FLAG': 101},
        'ilBonus': {'CHECK_SLA':101, 'GET_FLAG': 101, 'PUT_FLAG': 101},
    }
    """

    url = "http://10.10.0.1/api/reports/status.json"
    """
    {
        "currentRound":44,
        "firstBloods":[
            {
                "serviceShortname":"ilBonus",
                "teamId":47,
                "timestamp":"2023-05-20T08:02:05.897Z"
            }
        ]
    }
    """
    status = requests.get(url)
    while True:  # Wait if the network isn't open
        url = "http://10.10.0.1/api/reports/status.json"
        status = requests.get(url)
        if status.json() != {"code": "UNKNOWN", "message": "An error has occurred"}:
            break
        time.sleep(30)
        return
    if logger:
        logger.info("Game start")

    currentRound = status.json()["currentRound"]
    url = f"http://10.10.0.1/api/reports/public/{currentRound}/checks.json"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Check returned {response}")
    status_list = response.json()
    current_status = {}
    for s in status_list:
        # print(s)
        if s["exitCode"] not in [101, 104]:
            print(s["exitCode"], s["stdout"])
        if s["teamId"] != conf["team_id"]:
            continue
        service = s["serviceShortname"]
        action = s["action"]
        exitcode = s["exitCode"]  # 101 is ok, 104 is Flag Retrieve Failed

        try:
            current_status[service]
        except KeyError:
            current_status[service] = {}

        current_status[service][action] = exitcode

    print(current_status)
    return current_status


if __name__ == "__main__":
    scrape_status()
