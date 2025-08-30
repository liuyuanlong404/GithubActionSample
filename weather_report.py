import os
import requests
import json
import datetime

# 安全获取环境变量
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
open_ids_str = os.environ.get("OPEN_ID", "")
openIds = open_ids_str.split(",") if open_ids_str else []
weather_template_id = os.environ.get("TEMPLATE_ID")

if not all([appID, appSecret, openIds, weather_template_id]):
    raise EnvironmentError("请确保 APP_ID, APP_SECRET, OPEN_ID, TEMPLATE_ID 均已设置并非空值")

# 天气码对应的中文映射
WEATHER_CODE_MAP = {
    0: "晴",
    1: "少云",
    2: "多云",
    3: "阴",
    # 可自行扩展更多
}

def get_weather(city):
    city_coords = {"西安": {"latitude": 34.3416, "longitude": 108.9398}}
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
        print(r.text)
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
