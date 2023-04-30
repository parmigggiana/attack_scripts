from .common import *
import importlib
import os
import sys

importlib.reload(config)

exploits_dir = os.path.join(os.getcwd(), "exploits")
_exploits = [
    filename
    for filename in os.listdir(exploits_dir)
    if os.path.isfile(os.path.join(exploits_dir, filename))
    and filename not in ["common.py", "example.py"]
]

exploits = []
for exp in _exploits:
    name, ext = os.path.splitext(exp)
    if ext == ".py":
        full_path = os.path.join(exploits_dir, exp)
        importlib.import_module("." + name, "exploits")
        exploits.append(getattr(sys.modules["exploits." + name], name))


log.setLevel(config.log_level)  # debug, info, warning, error

# if exploits:
#    log.info(f"Loading exploits = {[x.__name__ for x in exploits]} ")
