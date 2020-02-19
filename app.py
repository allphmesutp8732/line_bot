from flask import Flask, request, abort
from datetime import datetime

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('qpWMu2KuLbVUwhLGyqiZKc0AVqoZwPKGJNw0aMjxAsmR9E1ZQ6h/7lhsQAlSN24Yf5tDBZ7xy6Bb7pryoXmD+6R7L4tor3O8csgz+jXW+4p2z68SvYq3sz3NY2J7gkVnLE1XiPclzMUmjAj3moFfmAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e262791ee0d485493cddece097761a9d')


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
    r = "請換句話說。"
    # if msg in ["Hi", "hi"]:
    #     r = "Hello~"
    # elif msg == "再見" or msg == "掰掰":
    #     r = "See Ya~"
    # elif msg == "現在時間" or msg == "現在幾點":
    #     now = datetime.now()
    #     r = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=r))


if __name__ == "__main__":
    app.run()