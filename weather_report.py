# 安装依赖 pip3 install requests html5lib bs4 schedule
import os
import requests
import json
from bs4 import BeautifulSoup
import datetime

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID，支持多个，用逗号分隔
openIds = os.environ.get("OPEN_ID").split(",")
# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID")


def get_weather(my_city):
    urls = [
        "http://www.weather.com.cn/textFC/hb.shtml",
        "http://www.weather.com.cn/textFC/db.shtml",
        "http://www.weather.com.cn/textFC/hd.shtml",
        "http://www.weather.com.cn/textFC/hz.shtml",
        "http://www.weather.com.cn/textFC/hn.shtml",
        "http://www.weather.com.cn/textFC/xb.shtml",
        "http://www.weather.com.cn/textFC/xn.shtml"
    ]
    for url in urls:
        resp = requests.get(url)
        text = resp.content.decode("utf-8")
        soup = BeautifulSoup(text, 'html5lib')
        div_conMidtab = soup.find("div", class_="conMidtab")
        tables = div_conMidtab.find_all("table")
        for table in tables:
            trs = table.find_all("tr")[2:]
            for tr in trs:
                tds = tr.find_all("td")
                city_td = tds[-8]
                this_city = list(city_td.stripped_strings)[0]
                if this_city == my_city:
                    high_temp_td = tds[-5]
                    low_temp_td = tds[-2]
                    weather_type_day_td = tds[-7]
                    weather_type_night_td = tds[-4]
                    wind_td_day = tds[-6]
                    wind_td_day_night = tds[-3]

                    high_temp = list(high_temp_td.stripped_strings)[0]
                    low_temp = list(low_temp_td.stripped_strings)[0]
                    weather_typ_day = list(weather_type_day_td.stripped_strings)[0]
                    weather_type_night = list(weather_type_night_td.stripped_strings)[0]

                    wind_day = "".join(list(wind_td_day.stripped_strings))
                    wind_night = "".join(list(wind_td_day_night.stripped_strings))

                    temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                    weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                    wind = wind_day if wind_day != "--" else wind_night
                    return this_city, temp, weather_typ, wind


def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    response = requests.get(url).json()
    print(response)
    return response.get('access_token')


def get_daily_love():
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = r.json()
    return all_dict['returnObj'][0]


def send_weather(access_token, open_id, weather):
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    body = {
        "touser": open_id.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {"value": today_str},
            "region": {"value": weather[0]},
            "weather": {"value": weather[2]},
            "temp": {"value": weather[1]},
            "wind_dir": {"value": weather[3]},
            "today_note": {"value": get_daily_love()}
        }
    }
    url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
    print(requests.post(url, json.dumps(body)).text)


def weather_report(this_city):
    access_token = get_access_token()
    weather = get_weather(this_city)
    print(f"天气信息： {weather}")
    for open_id in openIds:
        send_weather(access_token, open_id, weather)


if __name__ == '__main__':
    weather_report("西安")
