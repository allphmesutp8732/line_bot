from __future__ import unicode_literals
from flask import Flask, request, abort, render_template
from datetime import datetime

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ImageMessage, ImageSendMessage
)
import configparser
import urllib
import re
import random
import json
import requests

app = Flask(__name__)


# Line 聊天機器人基本資料
config = configparser.ConfigParser()
config.read('config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'access_token'))
handler = WebhookHandler(config.get('line-bot', 'WebHook_handler'))

# 接收 Line 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def GetWeather(station):
    end_point = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=CWB-C6C22A6C-B350-4583-A765-D34DC7A98E1D"
    data = requests.get(end_point).json()
    data = data["records"]["location"]

    target_station = "not found"
    for item in data:
        if item["locationName"] == str(station):
            target_station = item
        # else:
        #     end_point = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=CWB-C6C22A6C-B350-4583-A765-D34DC7A98E1D"
        #     data = requests.get(end_point).json()
        #     data = data["records"]["location"]
        #     for i in data:
        #         if i["locationName"] == str(station):
        #             target_station = item
    return target_station

def MakeWeather(station):
    WeatherData = GetWeather(station)
    if WeatherData == "not found":
        return False

    City = WeatherData["parameter"]
    WeatherData = WeatherData["weatherElement"]
    City = City[0]["parameterValue"]
    City_cast = ""
    msg = "花花天氣報告 - " + station + "測站"
    msg += "\n\n氣溫 = " + WeatherData[3]["elementValue"] + "℃\n"
    msg += "濕度 = " + \
        str(float(WeatherData[4]["elementValue"]) * 100) + "% RH\n"
    msg += "累積雨量 = " + WeatherData[6]["elementValue"] + "mm\n"
    end_point2 = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-C6C22A6C-B350-4583-A765-D34DC7A98E1D"
    forecast_data = requests.get(end_point2).json()
    forecast_data = forecast_data["records"]["location"]
    for item in forecast_data:
        if item["locationName"] == City:
            City_cast = item["weatherElement"]
    msg += "\n天氣預報：\n"
    f_time = City_cast[0]["time"]
    f_PoP = City_cast[1]["time"]
    f_maxT = City_cast[4]["time"]
    f_minT = City_cast[2]["time"]
    msg += f_time[0]["startTime"] + " ~ " + f_time[0]["endTime"] + " : "
    msg += f_time[0]["parameter"]["parameterName"] + " 降雨機率： " + f_PoP[0]["parameter"]["parameterName"] + " % "
    msg += "\n 最高溫 " + f_maxT[0]["parameter"]["parameterName"] + "最低溫 " + f_minT[0]["parameter"]["parameterName"]+ " \n"
    msg += f_time[1]["startTime"] + " ~ " + f_time[1]["endTime"] + " : "
    msg += f_time[1]["parameter"]["parameterName"] + " 降雨機率： " + f_PoP[1]["parameter"]["parameterName"] + " % "
    msg += "\n 最高溫 " + f_maxT[1]["parameter"]["parameterName"] + "最低溫 " + f_minT[1]["parameter"]["parameterName"]+ " \n"
    return msg

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('Handle: reply_token: ' + event.reply_token + ', message: ' + event.message.text)
    msg = event.message.text
    msg_weather = event.message.text.split(' ')

    if msg_weather[0] == '天氣':
        station = msg_weather[1]
        WeatherMsg = MakeWeather(station)

        if not WeatherMsg:
            WeatherMsg = "找不到這個氣象站"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=WeatherMsg))
        return

    r = '看不懂，請換句話說。'
    if '貼圖' in msg:
        sticker_message = StickerSendMessage(
            package_id = '1',
            sticker_id = '1'
        )

        line_bot_api.reply_message(
        event.reply_token,
        sticker_message)
        return

    if 'Hi' in msg or 'hi' in msg:
        r = 'Hello~'
    elif '再見' in msg or '掰掰' in msg or 'bye' in msg or 'Bye' in msg:
        r = 'See Ya~'
    elif '現在時間' in msg or '現在幾點' in msg:
        now = datetime.now().ctime()
        r = str((now.hour+8)%24) + ':' + str(now.minute) + ':' + str(now.second)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=r))


if __name__ == "__main__":
    app.run()