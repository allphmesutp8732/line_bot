from __future__ import unicode_literals
from flask import Flask, request, abort, render_template
from datetime import datetime,timezone,timedelta

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

import ssl
import time
from linebot.models import *
import configparser
import urllib
import re
import random
import json
import requests
import os

app = Flask(__name__)

sticker_ids = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 21, 100, 101, 102, 103, 106, 107, 110, 114, 116, 117, 119, 120, 122, 124, 125, 130, 134, 136, 137, 138, 139, 402, 20, 22, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 156, 157, 158, 159, 160, 151, 164, 166, 167, 171, 172, 176, 179, 501, 504, 505, 506, 508, 509, 511, 512, 513, 514, 516]
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
    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def GetWeather(station):
    #自動測站
    end_point = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-C6C22A6C-B350-4583-A765-D34DC7A98E1D"
    data = requests.get(end_point).json()
    data = data["records"]["location"]

    target_station = "not found"
    for item in data:
        if item["locationName"] == str(station):
            target_station = item
            return target_station
            continue

    #人工測站        
    end_point = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=CWB-C6C22A6C-B350-4583-A765-D34DC7A98E1D"
    data = requests.get(end_point).json()
    data = data["records"]["location"]
    for item in data:
        if item["locationName"] == str(station):
            target_station = item
            return target_station
            continue
    return target_station

def MakeWeather(station):
    WeatherData = GetWeather(station)
    if WeatherData == "not found":
        return False

    
    msg = "花花天氣報告 - " + station + "測站"
    msg += "\n最後觀測時間：" + WeatherData["time"]["obsTime"]
    City = WeatherData["parameter"]
    WeatherData = WeatherData["weatherElement"]
    City = City[0]["parameterValue"]
    City_cast = ""
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
    msg += "\n縣市天氣預報：\n"
    f_time = City_cast[0]["time"]
    f_PoP = City_cast[1]["time"]
    f_maxT = City_cast[4]["time"]
    f_minT = City_cast[2]["time"]
    msg += f_time[0]["startTime"] + " ~ " + f_time[0]["endTime"] + " : \n"
    msg += f_time[0]["parameter"]["parameterName"] + " 降雨機率：" + f_PoP[0]["parameter"]["parameterName"] + " % "
    msg += "最高溫 " + f_maxT[0]["parameter"]["parameterName"] + " 最低溫 " + f_minT[0]["parameter"]["parameterName"]+ " \n"
    msg += f_time[1]["startTime"] + " ~ " + f_time[1]["endTime"] + " : \n"
    msg += f_time[1]["parameter"]["parameterName"] + " 降雨機率：" + f_PoP[1]["parameter"]["parameterName"] + " % "
    msg += "最高溫 " + f_maxT[1]["parameter"]["parameterName"] + " 最低溫 " + f_minT[1]["parameter"]["parameterName"]+ " \n"
    return msg

def CurrencyExchange(currency_index):
    msg = "目前匯率：（台幣：" + currency_index + "） = 1 :"
    data = requests.get('https://tw.rter.info/capi.php').json()
    usdtwd = data["USDTWD"]["Exrate"]
    time = data["USDTWD"]["UTC"]
    currency_dict = {"美金" : "USD", "日幣" : "JPY", "人民幣" : "CNY", "港幣" : "HKD", "歐元" : "EUR", "韓元" : "KRW", "英鎊" : "GBP"}
    currency_index = "USD" + currency_dict[currency_index]
    if currency_index == "USDUSD":
        exrate = 1 / float(usdtwd)
    else:
        Exd = data[currency_index]
        exrate = 1 / float(usdtwd) * float(Exd["Exrate"])
        time = Exd["UTC"]
    msg += str(exrate) + '\n'
    msg += "最後更新時間：UTC" 
    msg += str(time)
    return msg

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('Handle: reply_token: ' + event.reply_token + ', message: ' + event.message.text)
    user_id = event.source.user_id
    print("user_id = ",user_id)
    profile = line_bot_api.get_profile(user_id, timeout = None)
    user_name = profile.display_name
    msg = event.message.text
    msg_weather = msg.split(' ')
    msg_currency = msg_weather
    r = '看不懂，請換句話說。'
    if "自我介紹" in msg or "help" in msg:
        r = "哈囉～" + user_name + "! 歡迎使用本聊天機器人\n"
        r += "您可以使用本聊天機器人進行\n<1> 天氣查詢（輸入：天氣 (測站名））\n<2> 匯率查詢（輸入：匯率）\n<3> 時間查詢（輸入：現在時間）\n<4> 基本對話等"
    #查詢天氣
    if msg_weather[0] == '天氣':
        if len(msg_weather) == 1:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你沒輸入測站啊！！！"))
            return
        elif len(msg_weather) > 2:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你亂輸入測站啊！！！"))
            return
        
        station = msg_weather[1]
        if station[0] == "台":
            station = "臺" + station[1:]
        WeatherMsg = MakeWeather(station)

        if not WeatherMsg:
            WeatherMsg = "找不到這個氣象站"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=WeatherMsg))
        return
    #傳送貼圖
    if '貼圖' in msg:
        index_id = random.randint(0, len(sticker_ids) - 1)
        sticker_id = str(sticker_ids[index_id])
        print("index_id = ",index_id)
        if index_id < 34:
            sticker_message = StickerSendMessage(
                package_id='1',
                sticker_id=sticker_id
                )
        else:
            sticker_message = StickerSendMessage(
                package_id='2',
                sticker_id=sticker_id
                )
        line_bot_api.reply_message(
            event.reply_token,
            sticker_message)
        return
    #查詢匯率
    if "匯率" in msg or "currency" in msg or "Currency" in msg:
        if len(msg_currency) == 1: #使用者僅輸入「匯率」
            print ("Currency selection.")
            buttons_template = ButtonsTemplate(
            title='請選擇要查詢的匯率',
            text='系統將回傳最新匯率資料，此為平均數值，詳細匯率請洽各大銀行官方告示。',
            thumbnail_image_url='https://www.advisor.ca/wp-content/uploads/sites/5/2018/07/different-world-currencies.jpg',
            actions=[
                PostbackTemplateAction(
                    label='美金',
                    text='匯率 美金',
                    data='USD'
                ),
                PostbackTemplateAction(
                    label='日幣',
                    text='匯率 日幣',
                    data='JPY'
                ),
                PostbackTemplateAction(
                    label='人民幣',
                    text='匯率 人民幣',
                    data='CNY'
                ),
                PostbackTemplateAction(
                    label='其他',
                    text='匯率 其他',
                    data='other'
                )
                ]
            )
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text="請選擇要查詢的匯率",
                    template=buttons_template
                ))
            return
        else: #使用者有輸入貨幣名或點選 Template 上的其他鈕
            if msg_currency[1] == "其他":
                print("Currency Selection - More.")
                buttons_template = ButtonsTemplate(
                    title='請選擇要查詢的匯率',
                    text='系統將回傳最新匯率資料，此為平均數值，詳細匯率請洽各大銀行官方告示。',
                    thumbnail_image_url='https://www.advisor.ca/wp-content/uploads/sites/5/2018/07/different-world-currencies.jpg',
                    actions=[
                    PostbackTemplateAction(
                        label='港幣',
                        text='匯率 港幣',
                      data='HKD'
                    ),
                    PostbackTemplateAction(
                        label='歐元',
                        text='匯率 歐元',
                        data='EUR'
                    ),
                    PostbackTemplateAction(
                        label='韓元',
                        text='匯率 韓元',
                        data='KRW'
                    ),
                    PostbackTemplateAction(
                        label='英鎊',
                        text='匯率 英鎊',
                        data='GBP'
                    )
                    ]
                    )
                line_bot_api.reply_message(
                    event.reply_token,TemplateSendMessage(alt_text="請選擇要查詢的匯率",template=buttons_template))
                return
            else:
                c_index = msg_currency[1]
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = CurrencyExchange(c_index)))
            return 
        return    
    if msg_weather[0] == "barcode" or msg_weather[0] == "Barcode" or msg_weather[0] == "BARCODE":
        barcode_data = msg_weather[1]
        r = "https://barcode.tec-it.com/barcode.ashx?data=" + barcode_data + "&code=Code128&dpi=96&dataseparator="       
        # from selenium import webdriver
        # from selenium.webdriver.chrome.options import Options
        # import base64
        # options = Options()
        # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        # prefs = {'profile.default_content_setting_values':{'notification' : 2}}
        # options.add_experimental_option('prefs',prefs)
        # options.add_argument("--ignore-certificate-errors")
        # options.add_argument("--headless")
        # options.add_argument("--incognito")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # driver = webdriver.Chrome(options = options)
        # driver.get("https://barcode.tec-it.com/zh")
        # ssl._create_default_https_context = ssl._create_unverified_context
        # data = driver.find_element_by_xpath('/html/body/div[2]/div[3]/form/div[5]/div[1]/div/div[1]/div[3]/textarea')
        # data.clear()
        # data.send_keys(barcode_data)
        # press = driver.find_element_by_xpath('/html/body/div[2]/div[3]/form/div[5]/div[1]/div/div[3]/a').click()
        # time.sleep(2)
        # img = driver.find_element_by_xpath('//*[@id="infoTarget"]/div[1]/img').get_attribute('src')
        image_message = ImageSendMessage(original_content_url = r, preview_image_url = r)
        # r = driver.find_element_by_xpath('/html/body/div[2]/div[3]/form/div[7]/div[1]/a[3]')
        # driver.quit()
        line_bot_api.reply_message(event.reply_token,image_message)
        return

    #打招呼
    if 'Hi' in msg or 'hi' in msg or 'hello' in msg or 'Hello' in msg:
        r = 'Hello~' + user_name + '!'
    elif "嗨" in msg or '哈囉' in msg or '安安' in msg:
        r = "嗨嗨～" + user_name + "！"
    elif '再見' in msg or '掰掰' in msg:
        r = '掰哺～'
    elif 'bye' in msg or 'Bye' in msg:
        r = "See Ya~"
    #查詢時間
    elif '現在時間' in msg or '現在幾點' in msg or '現在時刻' in msg:
        now = datetime.utcnow().replace(tzinfo = timezone.utc).astimezone(timezone(timedelta(hours = 8)))
        r = "現在時間：" + now.strftime('%H:%M:%S')
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=r))

@handler.add(MessageEvent)
def handle_sticker_message(event, destination):
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print("index_id = ",index_id)
    if index_id < 34:
        sticker_message = StickerSendMessage(
            package_id='1',
            sticker_id=sticker_id
            )
    else:
        sticker_message = StickerSendMessage(
            package_id='2',
            sticker_id=sticker_id
            )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)

if __name__ == "__main__":
    app.run()