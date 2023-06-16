from requests import get


def isnetworkopen():
    url = "http://10.10.0.1/api/reports/status.json"
    status = get(url)
    if status.json() == {"code": "UNKNOWN", "message": "An error has occurred"}:
        return False
    else:
        return True
