from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import re, tempfile
from imgurpython import ImgurClient

import schedule, time
import random, traceback
import game, lottery, send_push_message

import talk, script, eat

import json
from datetime import datetime
import sys
import pygsheets
import os


app = Flask(__name__)

#import database, googleSheet
'''
# Channel Access Token
line_bot_api = LineBotApi('N6auYEaF/2FjOkvLUGPZk31wz8HvrxRSv0dRnDYvlh8vV+JwZJVOdh/2Y10LWlBY5u/lSaRKy1FfEcFwKShMson03Te60PiUpWmAUEB/fNnWHAwDZrCzlp6JV+6b1sArj8kL/b52vDHXT/3KXlthqAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('b5f09601f13baf753a08b025c318f5c2')
'''
#ma_bot
# Channel Access Token
line_bot_api = LineBotApi(
    'OZaJksx8g/eZfwsV4abLZsoAjo51lCG5z61rx5RTG8xxxRZEuqn5675GIy7FoAaA6UfZtB/0gEDEbIGmK/7twYslMvdlnuNCcta3LbCGkRAvUWojkSKGOM1JdUOW1HlfTiQOPWSMCpRadcfMCcA7cwdB04t89/1O/w1cDnyilFU='
)
# Channel Secret
handler = WebhookHandler('86a1d36097bf45217576866b2ebc14f3')

# imgur key
'''
client_id = 'fa56d6b6417a3a4'
client_secret = '40a9335c64c2e50749927978663103e3a9cbd0f9'
album_id = 'DkD9rDb'
access_token = '5dc739693a8e98feccaebbb68084003c2e0cc280'
refresh_token = '663b65e5cc94cc3126b488cec5cde02510b97ae5'
'''
static_tmp_path = '.'
# google sheet

#url = 'https://notify-api.line.me/api/notify'
creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDS"))

with open('creds.json', 'w') as json_file:
    json.dump(creds_json, json_file, indent=4)  # indent 用於美化格式
# 使用 from_client_config 進行授權
gc = pygsheets.authorize(service_account_file="creds.json")
survey_url = 'https://docs.google.com/spreadsheets/d/1LffAHLYbv6bOgovVwmUZcBO2WzAy0WmxbNQx8wFHbhk/edit?usp=sharing'
sh = gc.open_by_url(survey_url)


# 監聽所有來自 /callback 的 Post Request
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


# 處理Postback
@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        replyMessageList = []
        
        #if len(replyMessageList) == 0:
        #    replyMessageList += script.getResponsePostback(event)
        if len(replyMessageList) == 0:
            replyMessageList += game.getResponsePostback(event, line_bot_api)
        if len(replyMessageList) != 0:
            #print(replyMessageList)
            line_bot_api.reply_message(event.reply_token, replyMessageList)

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        
        replyMessageList = []
        
        #if len(replyMessageList) == 0:
        #    replyMessageList += eat.getResponse(event)
        if len(replyMessageList) == 0:
            send_push_message.getResponse(event,line_bot_api,sh)
        if len(replyMessageList) == 0:
            replyMessageList += game.getResponse(event, line_bot_api, sh)
        if len(replyMessageList) == 0:
            replyMessageList += lottery.getResponse(event)
        if len(replyMessageList) != 0:
            line_bot_api.reply_message(event.reply_token, replyMessageList)

    except LineBotApiError as e:
        line_bot_api.reply_message(event.reply_token,
                                   TextMessage(text="error1"))
        error = '''LineBotApiError\n''' + e.__str__()
        ws = sh.worksheet_by_title('測試')
        ws.cell((5,5)).set_value(error)
        #googleSheet.uploadException(error)
        return
    except:
        line_bot_api.reply_message(event.reply_token,
                                   TextMessage(text="error2"))
        error = '''UnknownError\n''' + traceback.format_exc()
        ws = sh.worksheet_by_title('測試')
        ws.cell((6,6)).set_value(error)
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    try:
        # replymes = 'Type:' + str(event.message.type)
        # replymes += '\nId:' + str(event.message.id)
        # replymes += '\nTitle:' + str(event.message.title)
        # replymes += '\nAddress:\n' + str(event.message.address)
        # replymes += '\nLatitude:' + str(event.message.latitude)
        # replymes += '\nLongitude:' + str(event.message.longitude)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

        replyMessageList = []

        if len(replyMessageList) == 0:
            replyMessageList += eat.getResponseLocation(event)
        if len(replyMessageList) != 0:
            line_bot_api.reply_message(event.reply_token, replyMessageList)

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\npackage_id:' + str(event.message.package_id)
        replymes += '\nsticker_id:\n' + str(event.message.sticker_id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        message_content = line_bot_api.get_message_content(event.message.id)

        ### ma
        '''
        ext = 'jpg'
        with tempfile.NamedTemporaryFile(dir=static_tmp_path,
                                         prefix=ext + '-',
                                         delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)

        try:
            client = ImgurClient(client_id, client_secret, access_token,
                                 refresh_token)
            config = {
                'album': album_id,
                'name': 'Catastrophe!',
                'title': 'Catastrophe!',
                'description': 'Cute kitten being cute on '
            }
            path = os.path.join('.', dist_name)
            client.upload_from_path(path, config=config, anon=False)
            os.remove(path)
            print(path)
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='上傳成功'))
        except:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='上傳失敗'))
        return 0
        '''
        #line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\nDuration:' + str(event.message.duration)
        message_content = line_bot_api.get_message_content(event.message.id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\nDuration:' + str(event.message.duration)
        message_content = line_bot_api.get_message_content(event.message.id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


@handler.add(MessageEvent, message=FileMessage)
def handle_file(event):
    try:
        replymes = 'Type:' + str(event.message.type)
        replymes += '\nId:' + str(event.message.id)
        replymes += '\nfile_size:' + str(event.message.file_size)
        replymes += '\nfile_name:' + str(event.message.file_name)
        message_content = line_bot_api.get_message_content(event.message.id)
        # line_bot_api.reply_message(event.reply_token, TextMessage(text=replymes))

    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return


# 定義一個函數來在背景執行 schedule.run_pending
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分鐘檢查一次任務
        print('60000000000000000')
if __name__ == "__main__":
    # 創建並啟動一個線程來運行 run_schedule
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True  # 設置為守護線程，這樣當主程式結束時該線程會自動終止
    schedule_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
