import os
import requests
import json
import datetime

# 从环境变量获取配置
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openIds = os.environ.get("OPEN_ID").split(",")
weather_template_id = os.environ.get("TEMPLATE_ID")

def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID}&secret={appSecret}'
    response = requests.get(url).json()
    return response.get('access_token')

def send_weather(access_token, open_id, weather):
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    body = {
        "touser": open_id.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {"value": today_str},
            "region": {"value": weather["city"]},
            "weather": {"value": weather["weather"]},
            "temp": {"value": weather["temperature"]},
            "wind_dir": {"value": weather["wind_speed"]},
            "today_note": {"value": "今天也要加油哦！"}
        }
    }
    url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
    response = requests.post(url, json.dumps(body))
    print(response.text)

def weather_report(city):
    access_token = get_access_token()
    weather = get_weather(city)
    if weather:
        for open_id in openIds:
            send_weather(access_token, open_id, weather)
    else:
        print(f"无法获取 {city} 的天气信息")

if __name__ == '__main__':
    weather_report("西安")
