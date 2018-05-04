import tempfile
import os
import sys
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,LineBotApiError
)
from linebot.models import (
   MessageEvent, TextMessage, TextSendMessage,
   ImageMessage, VideoMessage, AudioMessage,
   StickerMessage,JoinEvent,StickerSendMessage,
   SourceGroup

)

from features.CarAnalytics import LicencePlate
import priceOil



static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
app = Flask(__name__)

latest_image_path = ''

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
   print('Specify LINE_CHANNEL_SECRET as environment variable.')
   sys.exit(1)
if channel_access_token is None:
   print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
   sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
# app = app.py
#line_bot_api = LineBotApi('tGrHUoFxl0n9SUpbKuOZBeJwNNya1AiUaYJ+I5rP/+JKQoMDdbzOWM0PN8eMJBNB16WbbR7XhicF/r2kDycOMZYX2ZYOXvczKjDqXGgp7IDNkoPyCFIeMuxiYDq2ErUtApA13UmQG+YAiU9RzksJEgdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('dc13dab5ccf46f841311a296443207d0')
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

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # Handle webhook verification
    if event.reply_token == 'ffffffffffffffffffffffffffffffff':
       return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global latest_image_path
    
    # Handle webhook verification
    if event.reply_token == '00000000000000000000000000000000':
        return 'OK'
    if event.message.text == 'ออกไปได้แล้ว':
        if isinstance(event.source,SourceGroup) and event.source.user_id == 'U792ff52513700854a4a20721b90e79fb':
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text='บะบายค่า')
            )   
            line_bot_api.leave_group(event.source.group_id)
        else:
               line_bot_api.reply_message(
                   event.reply_token,
                   TextMessage(text='ไม่ออกอะจ้าาา!')
               )
    elif event.message.text == 'profile':
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        # image_message = ImageSendMessage(
        #             original_content_url=profile.picture_url,
        #             preview_image_url=profile.picture_url
        #         )

        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=profile.display_name),
                TextSendMessage(text=profile.user_id),
                TextSendMessage(text=profile.picture_url),
                TextSendMessage(text=profile.status_message),
                # image_message
            ]
        )
    elif (event.message.text == 'ราคาน้ำมัน') or (event.message.text == 'oilPrice') :
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
        #line_bot_api.push_message(
            #event.reply_token,
            # TextSendMessage(text=event.message.text+'จ๋าาา'))
            #TextSendMessage(text='เราไม่เข้าใจนายอะ ลองใส่เป็น ราคาน้ำมัน หรือ oilPrice นะค่ะ')
        #)
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text='ไม่เข้าใจอะ')
        ) 






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

@handler.add(JoinEvent)
def handle_join(event):
    # group_id = event.source.group_id
    # line_bot_api.get_group_member_profile(group_id,member_id)
    # member_ids_res = line_bot_api.get_group_member_ids(group_id)
    # print(member_ids_res.member_ids)
    # print(member_ids_res.next)

    try:
        profile = line_bot_api.get_group_member_profile(
            event.source.group_id,
            'U792ff52513700854a4a20721b90e79fb'
        )
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text='สวัสดีค่า'),
                StickerSendMessage(
                    package_id=1,
                    sticker_id=2
                )
            ]
        )        
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text='หัวหน้าไม่อยู่ในห้องนี้\nไปละค่ะ\nบัย'),
            ]
        )
        line_bot_api.leave_group(event.source.group_id)

if __name__ == "__main__":
    app.run()