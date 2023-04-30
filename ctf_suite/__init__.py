from .common import *
import importlib
import os
import sys

exploits_dir = os.path.join(os.getcwd(), "config/exploits")
_exploits = [
    filename
    for filename in os.listdir(exploits_dir)
    if os.path.isfile(os.path.join(exploits_dir, filename))
    and filename not in ["__init__.py", "_common.py"]
]

exploits = []
for exp in _exploits:
    name = os.path.splitext(exp)[0]
    full_path = os.path.join(exploits_dir, exp)
    importlib.import_module("." + name, "config.exploits")
    # print(sys.modules["config.exploits." + name])
    exploits.append(getattr(sys.modules["config.exploits." + name], name))
exploits.remove(getattr(sys.modules["config.exploits.example"], "example"))
