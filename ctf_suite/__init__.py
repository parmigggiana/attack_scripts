from .common import *
import importlib
import os
import sys
import config

exploits_dir = os.path.join(os.getcwd(), "exploits")
_exploits = [
    filename
    for filename in os.listdir(exploits_dir)
    if os.path.isfile(os.path.join(exploits_dir, filename))
    and filename not in ["common.py", "example.py"]
]

exploits = []
for exp in _exploits:
    name = os.path.splitext(exp)[0]
    full_path = os.path.join(exploits_dir, exp)
    importlib.import_module("." + name, "exploits")
    exploits.append(getattr(sys.modules["exploits." + name], name))
