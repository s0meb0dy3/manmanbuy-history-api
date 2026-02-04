import requests
import time
import hashlib
import re
import json
from datetime import datetime
from urllib.parse import quote

# ---------------- 1. 加密算法 (保持不变) ----------------
def generate_token(params):
    salt = "C5C3F201A8E8FC634D37A766A0299218"
    sorted_keys = sorted(params.keys())
    
    sign_str = salt
    for key in sorted_keys:
        val = str(params[key])
        # 保持 safe='' 以模拟 JS 行为
        encoded_val = quote(val, safe='') 
        sign_str += quote(key, safe='') + encoded_val

    sign_str += salt
    sign_str = sign_str.upper()
    token = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    return token.upper()

# ---------------- 2. 核心请求逻辑 ----------------
def _extract_first_timestamp(date_price):
    if isinstance(date_price, list):
        if not date_price:
            return None
        first = date_price[0]
        if isinstance(first, list) and first:
            return first[0]
        if isinstance(first, str):
            return int(first) if first.isdigit() else first
        if isinstance(first, (int, float)):
            return first
        return None

    if isinstance(date_price, str):
        s = date_price.strip()
        if not s:
            return None
        try:
            parsed = json.loads(s)
        except json.JSONDecodeError:
            try:
                parsed = json.loads(f"[{s}]")
            except json.JSONDecodeError:
                match = re.search(r"\d{10,13}", s)
                return int(match.group(0)) if match else None
        return _extract_first_timestamp(parsed)

    return None


def get_first_date_price_time(authentication, cookie, item_url):
    base_url = "https://tool.manmanbuy.com/api.ashx"

    local_ts = int(time.time() * 1000)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://tool.manmanbuy.com",
        "Referer": "https://tool.manmanbuy.com/HistoryLowest.aspx",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": authentication,
        "Cookie": cookie,
    }

    raw_params = {
        "method": "getHistoryTrend",
        "key": item_url,
        "t": str(local_ts),
    }

    token = generate_token(raw_params)
    raw_params["token"] = token

    response = requests.post(base_url, data=raw_params, headers=headers, timeout=15)
    response.raise_for_status()

    res_json = response.json()
    data = res_json.get("data") or {}
    date_price = data.get("datePrice")
    ts = _extract_first_timestamp(date_price)
    if ts is None:
        return None

    ts_val = int(ts)
    if ts_val >= 1_000_000_000_000:
        ts_val = ts_val / 1000

    return datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M:%S")


def fetch_data():
    base_url = "https://tool.manmanbuy.com/api.ashx"
    
    # 【步骤 A】先访问一次主页，获取服务器的 Date 头，或者直接粗略校准
    # 这里我们采用更直接的方法：手动微调。
    # 如果总是超时，试试把时间往后推迟一点点，或者直接用 standard time
    
    # 生成本地时间戳
    local_ts = int(time.time() * 1000)
    print(f"本地时间戳: {local_ts}")

    # 【重要】建议你在这里重新填入刚刚刷新浏览器抓到的 headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://tool.manmanbuy.com",
        "Referer": "https://tool.manmanbuy.com/HistoryLowest.aspx",
        "X-Requested-With": "XMLHttpRequest",
        # ！！！请务必刷新网页，填入最新的！！！
        "Authorization": "BasicAuth D8DD2812A942776A14827FEBD7330A8A170D3A78D93171824AD632794279B576E0F627B5F649AD5A22D6168F0F88C755FD6F939A7395A2736F7DA8F633B38C45BBF56123D83CFCCA6D9D1585D574A4C1",
        "Cookie": "ASP.NET_SessionId=d3hdhnmamly2zhe502iuuqla; ..." # 这里也要换新的
    }
    
    # 构造参数
    raw_params = {
        "method": "getHistoryTrend", 
        "key": "https://item.jd.com/10162975247259.html", 
        "t": str(local_ts)
    }
    
    # 计算 Token
    token = generate_token(raw_params)
    raw_params['token'] = token

    print("正在发送请求...")
    try:
        # 如果有代理，保持开启
        proxies = {

        }
        
        response = requests.post(base_url, data=raw_params, headers=headers, proxies=proxies)
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:100]}...")
        
        res_json = response.json()
        print(f"解析后的 JSON: {res_json}")

                
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    authentication = "BasicAuth D8DD2812A942776A14827FEBD7330A8A170D3A78D93171824AD632794279B576E0F627B5F649AD5A22D6168F0F88C755FD6F939A7395A2736F7DA8F633B38C450C18DB1C68D1547D246F075102A6012A"
    cookie = "ASP.NET_SessionId=d3hdhnmamly2zhe502iuuqla; ..."
    item_urls = [
        "https://item.jd.com/10162975247259.html",
        "https://item.jd.com/10162975247260.html",
        "https://item.jd.com/10168368021057.html",
    ]

    for item_url in item_urls:
        try:
            readable_time = get_first_date_price_time(authentication, cookie, item_url)
            print(f"{item_url} -> {readable_time}")
        except Exception as e:
            print(f"{item_url} -> 错误: {e}")
