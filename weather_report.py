
import requests
import json
import datetime
import os

# 安全获取环境变量
appID = os.environ.get("APP_ID") or "wxcb0238c067975d0a"
appSecret = os.environ.get("APP_SECRET") or "9d73a1fd54dca9020b46ed1aa3a4aa62"
open_ids_str = os.environ.get("OPEN_ID", "")
openIds = open_ids_str.split(",") if open_ids_str else ["oq9fW18W9zpRZK0YGGJ5wDG1eSTw","oq9fW19xEBnle_wwSwAxh6XMoaes"]
weather_template_id = os.environ.get("TEMPLATE_ID") or "IYhfY5YqYRMb0daegwAWlpFTWJsYUqErBll_b5fZi80"

# 检查必要配置
if not appID or not appSecret or not weather_template_id:
    raise EnvironmentError("请确保 APP_ID, APP_SECRET, TEMPLATE_ID 均已设置并非空值")
if not openIds:
    print("警告: OPEN_ID 未设置，将使用默认值")

# 天气码对应的中文映射 (WMO天气代码)
WEATHER_CODE_MAP = {
    0: "晴",
    1: "少云",
    2: "多云",
    3: "阴",
    45: "雾",
    48: "霜雾",
    51: "毛毛雨",
    53: "小雨",
    55: "中雨",
    56: "冻毛毛雨",
    57: "冻雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "小阵雨",
    81: "中阵雨",
    82: "大阵雨",
    85: "小阵雪",
    86: "大阵雪",
    95: "雷雨",
    96: "雷雨伴冰雹",
    99: "强雷雨伴冰雹"
}

def get_weather(city):
    city_coords = {
        "西安": {"latitude": 34.3416, "longitude": 108.9398},
        "北京": {"latitude": 39.9042, "longitude": 116.4074},
        "上海": {"latitude": 31.2304, "longitude": 121.4737},
        "广州": {"latitude": 23.1291, "longitude": 113.2644},
        "深圳": {"latitude": 22.3193, "longitude": 114.1694},
        "杭州": {"latitude": 30.2741, "longitude": 120.1551},
        "成都": {"latitude": 30.5728, "longitude": 104.0668},
        "武汉": {"latitude": 30.5928, "longitude": 114.3055},
        "南京": {"latitude": 32.0603, "longitude": 118.7969},
        "天津": {"latitude": 39.3434, "longitude": 117.3616}
    }
    coords = city_coords.get(city)
    if not coords:
        return None
    try:
        resp = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={coords['latitude']}&longitude={coords['longitude']}&current_weather=true",
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"获取天气失败: {e}")
        return None

    cw = data.get("current_weather")
    if not cw:
        return None

    code = cw.get("weathercode")
    desc = WEATHER_CODE_MAP.get(code, f"天气码 {code}")
    return {
        "city": city,
        "temperature": f"{cw.get('temperature')}°C",
        "weather": desc,
        "wind_speed": f"{cw.get('windspeed')} km/h"
    }

def get_access_token():
    try:
        r = requests.get(
            f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID}&secret={appSecret}",
            timeout=5
        )
        r.raise_for_status()
        data = r.json()
        return data.get('access_token')
    except Exception as e:
        print(f"获取 access_token 失败: {e}")
        return None

def send_weather(token, open_id, weather):
    if not token:
        print("无效 access_token，跳过发送")
        return
    today = datetime.date.today().strftime("%Y年%m月%d日")
    body = {
        "touser": open_id.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {"value": today},
            "region": {"value": weather["city"]},
            "weather": {"value": weather["weather"]},
            "temp": {"value": weather["temperature"]},
            "wind_dir": {"value": weather["wind_speed"]},
            "today_note": {"value": "今天也要加油哦！"}
        }
    }
    try:
        r = requests.post(
            f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}',
            json=body,
            timeout=5
        )
        result = r.json()
        if result.get("errcode") != 0:
            print(f"消息发送失败: {result.get('errmsg')}")
        else:
            print(f"消息发送成功给 {open_id}")
    except Exception as e:
        print(f"发送消息失败: {e}")

def weather_report(city):
    token = get_access_token()
    weather = get_weather(city)
    if not weather:
        print(f"无法获取 {city} 的天气信息")
        return
    for oid in openIds:
        send_weather(token, oid, weather)

if __name__ == '__main__':
    weather_report("西安")
