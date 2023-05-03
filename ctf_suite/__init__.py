from .common import *
from .decorators import *
from .db import *
from ._exploits import exploits, exploitsNumber
import config

iplist = [  # except nopteam and teamip
    config.baseip.format(id=id)
    for id in range(1, config.highest_id + 1)
    if id != config.team_id
]

threadsNumber = len(iplist) * exploitsNumber

log.setLevel(
    config.log_level
)  # this is not best practice, ideally we shouldn't set this in library but it's a quick fix for live reloading the config
