from requests import get, ConnectTimeout

_NETOPEN = False


def isnetworkopen():
    global _NETOPEN

    if _NETOPEN:
        return True

    url = "http://10.10.0.1/api/reports/status.json"
    try:
        status = get(url, timeout=5)
        if status.json() != {"code": "UNKNOWN", "message": "An error has occurred"}:
            _NETOPEN = True
    except ConnectTimeout:  # This is mainly for testing
        _NETOPEN = True

    return _NETOPEN
