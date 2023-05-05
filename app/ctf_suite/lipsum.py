from math import ceil


import random

_separator = "\n"
_phrases = [
    "Jesse! We have to cook",
    "Jesus Christ Marie! They're Minerals!",
    "Yeah Mr. White! Yeah, science!",
]


def lipsum(length: int) -> str:
    ret = (_phrases * ceil(length / len(_phrases)))[:length]
    return _separator.join(random.sample(ret, length))


def napolipsum(length: int) -> str:
    if length <= 0:
        return ""
    ret = r"FORZANAPOLI" + napolipsum(length - 11)
    return ret[:length]


def test():
    print(napolipsum(20))
    print(lipsum(15))


if __name__ == "__main__":
    test()
