import tempfile
import os
import sys
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,VideoMessage,AudioMessage
)

from features.CarAnalytics import LicencePlate
import priceOil



static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
app = Flask(__name__)

latest_image_path = ''
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
    global latest_image_path
    if (event.message.text == 'ราคาน้ำมัน') or (event.message.text == 'oilPrice') :
        l = priceOil.get_price()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n"%(p[0],p[1])
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=s))
    elif (event.message.text == 'ตรวจสอบรถ') :

        line_bot_api.reply_message(
            event.reply_token,[
                TextSendMessage(text='รอแปบ นะค่ะ')
            ])
        #process image
        try:
            lp = LicencePlate()
            result = lp.process(latest_image_path)
            s = lp.translate(result)

            line_bot_api.push_message(
                event.source.user_id, [
                TextSendMessage(text=s),
                ])
        except Exception as e:
            print('Exception:',type(e),e)
            line_bot_api.push_message(
                event.source.user_id, [
                TextSendMessage(text='ไม่สามารถตรวจสอบได้ค่ะ รูปอาจจะมีความระเอียดต่ำไป')
                ])

    else:
        line_bot_api.push_message(
            event.reply_token,
            # TextSendMessage(text=event.message.text+'จ๋าาา'))
            TextSendMessage(text='เราไม่เข้าใจนายอะ ลองใส่เป็น ราคาน้ำมัน หรือ oilPrice นะค่ะ'))






# Other Message Type  s
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    global latest_image_path
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)
    

        #save image path
        latest_image_path = dist_path
        line_bot_api.reply_message(
            event.reply_token,[
                TextSendMessage(text= 'เก็บรูปให้แล้วค่ะ')
            ])



if __name__ == "__main__":
    app.run()