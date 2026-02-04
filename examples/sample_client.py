import hashlib
import time
from urllib.parse import quote

import requests


def generate_token(params):
    salt = "C5C3F201A8E8FC634D37A766A0299218"
    sign_str = salt
    for key in sorted(params.keys()):
        val = str(params[key])
        sign_str += quote(key, safe="") + quote(val, safe="")
    sign_str += salt
    sign_str = sign_str.upper()
    token = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
    return token.upper()


def call_api(authentication, cookie, item_url):
    base_url = "https://tool.manmanbuy.com/api.ashx"
    local_ts = int(time.time() * 1000)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://tool.manmanbuy.com",
        "Referer": "https://tool.manmanbuy.com/HistoryLowest.aspx",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": authentication,
        "Cookie": cookie,
    }

    params = {
        "method": "getHistoryTrend",
        "key": item_url,
        "t": str(local_ts),
    }
    params["token"] = generate_token(params)

    response = requests.post(base_url, data=params, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()


def main():
    authentication = "BasicAuth EXAMPLE_AUTH_VALUE"
    cookie = "ASP.NET_SessionId=EXAMPLE_SESSION_ID; ..."
    item_url = "https://item.jd.com/1234567890.html"

    result = call_api(authentication, cookie, item_url)
    print(result)


if __name__ == "__main__":
    main()
