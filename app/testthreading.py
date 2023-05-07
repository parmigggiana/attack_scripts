"""
$ time python testthreading.py # with n = 10_000_000
________________________________________________________
Executed in  283.61 millis    fish           external
   usr time  154.92 millis    0.00 micros  154.92 millis
   sys time  127.71 millis  661.00 micros  127.05 millis


$ time python testthreading.py # with n = 100 * 80
________________________________________________________
Executed in   71.82 millis    fish           external
   usr time  122.63 millis  347.00 micros  122.28 millis
   sys time   44.16 millis  140.00 micros   44.02 millis

"""
import itertools

from threading import Thread

from milkman.exploits import Exploits
from milkman.config import Config


def emptyfun(target_ip, exploit):
    return target_ip, exploit


n = 100 * 80  # 10_000_000
conf = Config()
tasks = []
exploits = Exploits()

for exploit, id in itertools.product(exploits, range(n)):
    target_ip = conf["baseip"].format(id=id)
    t = Thread(
        target=emptyfun,
        args=(target_ip, exploit),
        name=f"{exploit}_{target_ip}",
    )
    tasks.append(t)
    t.start()
for t in tasks:
    t.join()
