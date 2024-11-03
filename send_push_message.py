# send_push_message.py

from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
import json
import pygsheets

#url = 'https://notify-api.line.me/api/notify'
creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDS"))

with open('creds.json', 'w') as json_file:
    json.dump(creds_json, json_file, indent=4)  # indent 用於美化格式
# 使用 from_client_config 進行授權
gc = pygsheets.authorize(service_account_file="creds.json")
survey_url = 'https://docs.google.com/spreadsheets/d/1LffAHLYbv6bOgovVwmUZcBO2WzAy0WmxbNQx8wFHbhk/edit?usp=sharing'
sh = gc.open_by_url(survey_url)

def send_push_message():
    line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
    ws = sh.worksheet_by_title('測試')
    USER_ID = ws.cell((3,1)).value
    message = TextSendMessage(text="早安！這是一則自動推播訊息")
    line_bot_api.push_message(USER_ID, message)
    
if __name__ == "__main__":
    send_push_message()
