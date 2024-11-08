import random, traceback, os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
#import database, googleSheet
import re
import pygsheets
import time, datetime, pytz
def getResponse(content, line_bot_api, sh):

    try:
        usertype = content.source.type
        if usertype is 'user':
            room_id = content.source.user_id
            profile = line_bot_api.get_profile(content.source.user_id)

        elif usertype is 'room':
            room_id = content.source.room_id
            profile = line_bot_api.get_room_member_profile(
                content.source.room_id, content.source.user_id)

        else:
            room_id = content.source.group_id
            profile = line_bot_api.get_group_member_profile(
                content.source.group_id, content.source.user_id)

        ws = sh.worksheet_by_title('聊天室資料')
        ws.cell((1,10)).set_value('=MATCH("'+room_id+'",A:A,0)')
        ws.refresh()
        if(ws.cell((1,10)).value=='#N/A'):
            ws.add_rows(1)
            L=len(ws.get_col(1,include_tailing_empty=False))
            ws.cell((L+1,1)).set_value(room_id)
            ws.cell((L+1,2)).set_value(profile.display_name)

        
        if type(content) == str:
            mes = content
        else:
            mes = content.message.text
        learntxt = re.split('[,，]', mes)

        if learntxt[0] == '自動發文' and (room_id=="U309aa4760e4ef8573c99603498ff2e7d" or room_id=="Uef044b9b8604272fe3880362423af848"):
            column_a_values = ws.get_col(1)  # A 欄為 1，傳回值為列表
            column_c_values = ws.get_col(3)  # C 欄為 3，傳回值為列表
            # 輸出結果
            for i in range(1,len(ws.get_col(1,include_tailing_empty=False))+1):
                if(ws.cell((i,4)).value=="T"):
                    message = TextSendMessage(text=ws.cell((i,3)).value)
                    line_bot_api.push_message(ws.cell((i,1)).value, message)
                    location_message = LocationSendMessage(
                        title=ws.cell((1,5)).value,
                        address=ws.cell((1,6)).value,
                        latitude=ws.cell((1,7)).value,
                        longitude=ws.cell((1,8)).value
                        )
                    line_bot_api.push_message(ws.cell((i,1)).value, location_message)
        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        ws = sh.worksheet_by_title('log')
        ws.add_rows(1)
        L=len(ws.get_col(1,include_tailing_empty=False))
        localtime = datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
        ws.cell((L+1,1)).set_value(localtime)
        ws.cell((L+1,2)).set_value(error)

        #googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        ws = sh.worksheet_by_title('log')
        ws.add_rows(1)
        L=len(ws.get_col(1,include_tailing_empty=False))
        localtime = datetime.datetime.fromtimestamp(time.time()).astimezone(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
        ws.cell((L+1,1)).set_value(localtime)
        ws.cell((L+1,2)).set_value(error)
        #googleSheet.uploadException(error)
        return []


def getResponsePostback(content, line_bot_api):
    try:
        usertype = content.source.type
        if usertype is 'user':
            room_id = content.source.user_id
            profile = line_bot_api.get_profile(content.source.user_id)

        elif usertype is 'room':
            room_id = content.source.room_id
            profile = line_bot_api.get_room_member_profile(
                content.source.room_id, content.source.user_id)

        else:
            room_id = content.source.group_id
            profile = line_bot_api.get_group_member_profile(
                content.source.group_id, content.source.user_id)

        if os.path.isfile(room_id + 'vote.txt'):
            string = re.split('[,，]', content.postback.data)
            num = string[1]
            vote = string[0]
            gameFile = open(room_id + 'vote.txt', 'a')
            gameFile.write(content.source.user_id + ',' + vote + ',' +
                           profile.display_name + ',' + "\n")
            gameFile.close()
        else:
            return [TextMessage(text="你來晚了，投票已過期了，滾~")]

        return []
    except LineBotApiError as e:
        error = '''LineBotApiError\n''' + e.__str__()
        #googleSheet.uploadException(error)
        return []
    except:
        error = '''UnknownError\n''' + traceback.format_exc()
        #googleSheet.uploadException(error)
        return []


def modifySTR(content, response):
    if type(content) == str:
        return response
    else:
        return [TextMessage(text=response)]
