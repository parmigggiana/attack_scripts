from .common import *
from .decorators import *
from .db import *
from .lipsum import lipsum
from ._exploits import exploits, exploitsNumber

import config

iplist = [  # except nopteam and teamip
    config.baseip.format(id=id)
    for id in range(1, config.highest_id + 1)
    if id != config.team_id
]

threadsNumber = len(iplist) * exploitsNumber
