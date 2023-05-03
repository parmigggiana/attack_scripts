# A collection of scripts to simplify testing and deploying attacks in attack-defence CTFs
All you need to do is write the exploit for a single target! `test_attack` will 
help you check that everything works as intended. Before every game tick, `deploy` dinamically loads the configuration and any new exploits. Easy to configure through `config.py`, with a dedicated thread for each attack against each target.
Configs and exploits are being watched and the program will automatically reload them when changed, no need to restart it (EXPLOITS RELOAD IS BROKEN, CONFIGS WORK).
## Requirements
- `docker compose` for simple MongoDB setup. Alternatively, you can host the database yourself.
- `pip install -r requirements.txt`

## Configuration
At the start of the challenge, remember to properly edit `config.py` 
```python
log_level = "debug" 
team_id = 77
highest_id = 1
TEAM_TOKEN = "b0d9d5b0307be878aa00e935e230d2d"
max_time = 6  # time for a single thread to issue a warning. It will still wait for it to complete
tick_duration = 20  # gametick duration
flag_regex = "[A-Z0-9]{31}="
baseip = "10.60.{id}.1"
db_url = "mongodb://localhost:27017/"
flag_submission_delay = (
    120  # Every 120 seconds all new flags are submitted to the gameserver
)

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
Edit every function printing to stdout so that it is surrounded by `l.acquire()` and `l.release()` (This is not essential, but with this many parallel processes and threads they sometimes print on the same line. It keeps the output tidy). 

4. Done! If `deploy.py` is already running it will automatically load all new exploits (BROKEN RIGHT NOW) before the next game tick (but don't forget to save the files lmao).

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

    
    """
    [ ATTACK LOGIC ...]
    
    """
    

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
    
    """
    [ ATTACK LOGIC ...]
    
    """

    l.acquire()
    log.success(f"{flags}")
    l.release()
    return flags
```

## TODO
- [ ] Add flag submission logic
- [ ] Fix live-updating configs and exploits
- [ ] Only reload modules on-demand, using [watchdog](https://pythonhosted.org/watchdog/quickstart.html#quickstart)
- [ ] Move from pwn.log to proper logging with handler to distinguis processes and threads
- [ ] Gracefully stop the program intercepting SIGINT
- [ ] Instead of using a timer, read the new gametick from tcpdumps/caronte/tulip. This would allow simpler reloading (just restart all the processes, we won't waste time since we won't have a timer anymore). This means much simpler and more robust synchronization. It's quite funky right now