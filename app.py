from flask import Flask, request, abort
from datetime import datetime

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
)
import configparser

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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
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
        now = datetime.now()
        r = str((now.hour+8)%24) + ':' + str(now.minute) + ':' + str(now.second)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=r))


if __name__ == "__main__":
    app.run()