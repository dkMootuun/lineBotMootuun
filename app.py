from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import priceOil

app = Flask(__name__)
# app = app.py
line_bot_api = LineBotApi('BQOyunikRw/9QAmpvamgIxg62I23/9AXs1skmMDGx2M2gRpvdvAMwBF2y0PhczRnRQkQ9HQaobs0Faq+5wu2F0UdhL9/xN1owhJn4n3jhvLtYnosrXPEKuL3k/5mHelUKMNLFPp1bMYv0nX4WdGg9wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9669a64ef354ce21d40b2dd7d774583f')
# copy from linebot

@app.route("/",methods=['GET'])
def default_action():
    return 'hello'

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
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if (event.message.text == 'ราคาน้ำมัน') or (event.message.text == 'oilPrice') :
        l = priceOil.get_price()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n"%(p[0],p[1])
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=s))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            # TextSendMessage(text=event.message.text+'จ๋าาา'))
            TextSendMessage(text='เราไม่เข้าใจนายอะ ลองใส่เป็น ราคาน้ำมัน หรือ oilPrice'))


if __name__ == "__main__":
    app.run()