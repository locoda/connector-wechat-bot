# coding=utf8
import itchat
from itchat.content import *

import hashlib
import random
import unicodedata
import requests
import json
import time
import threading

import apiai
#from google import google

from token import APIAI_TOKEN, TULING_TOKEN

def send_online_notification(name):
    memberList = itchat.search_friends(name = name)

    while True:
        for member in memberList:
            itchat.send('Now the time is: ' + time.strftime(
                '%y/%m/%d-%H:%M:%S', time.localtime()), member['UserName'])
            time.sleep(.5)
        time.sleep(1800)


def tuling_reply(msg_content, user_id):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : TULING_TOKEN,
        'info'   : msg_content,
        'userid' : user_id,
    }
    
    s = requests.post(apiUrl, data=data, verify=False).json()
    print 'return code: ' + str(s['code'])
    if s['code'] == 100000:
        return s['text']
    if s['code'] == 200000:
        return s['text'] + s['url']
    if s['code'] == 302000:
        news = s['list'][random.randint(0, len(s['list']) - 1)]
        return news['article'] + '\n' + news['detailurl']
    if s['code'] == 308000:
        menu = s['list'][random.randint(0, len(s['list']) - 1)]
        return menu['name'] + '\n' + menu['detailurl'] + '\n' + menu['info']


def apiai_reply(msg_content, user_id):
    print "try APIAI reply..."
    ai = apiai.ApiAI(APIAI_TOKEN)
    request = ai.text_request()
    request.lang = 'zh-CN'
    request.session_id = user_id
    request.query = msg_content
    response = request.getresponse()
    s = json.loads(response.read(), encoding='UTF-8')
    
    if s['result']['action'] == 'input.unknown':
        # if msg_content.decode("utf-8").find(u"普渡") > -1 or msg_content.decode("utf-8").find(u"普度") > -1:
        #     print "use Google result reply..."
        #     search_results = google.search(msg_content.decode("utf-8"))  
        #     res = search_results[0]
        #     result = res.name + '\n' + res.link + '\n' 
        #     res = search_results[1]
        #     result = result + '\n' + res.name + '\n' + res.link + '\n' 
        #     return result
        # else:
        print "use Tuling reply"
        return tuling_reply(msg_content, user_id)
    if s['status']['code'] == 200:
        print "use APIAI reply"
        print 'return code: ' + str(s['status']['code'])
        print 'return score: ' + str(s['result']['score'])
        return s['result']['fulfillment']['speech']


@itchat.msg_register(TEXT)
def purdue_reply(msg):
    itchat.send(apiai_reply(msg['Content'].encode('UTF-8'), msg['FromUserName']), msg['FromUserName'])


@itchat.msg_register(INCOME_MSG, isGroupChat=True)
def sys_reply(msg):
    if msg['MsgType'] == 10000 and msg['Content'].find(u'加入') > -1:
        itchat.send(tuling_reply('welcome'.encode('UTF-8'), 10000), msg['FromUserName'])
        itchat.send_image('welcome.jpg', msg['FromUserName'])


@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    if msg['isAt']:
        info = msg['Content'].encode('utf-8')
        info = unicodedata.normalize('NFKC', unicode(info, "utf-8"))
        # print "original msg:" + info
        atpos = info.find('@')
        spos = info.find(' ')
        # print str(atpos) + ", " + str(spos)
        info = (info[0:atpos] + info[spos+1:len(info)]).encode("utf-8")
        # print "processed msg:" + info
        userid = int(hashlib.sha1(msg['ActualNickName'].encode('utf-8')).hexdigest(), 16) % 65537
        print "userid: " + str(userid)
        itchat.send(apiai_reply(info, userid), msg['FromUserName'])


itchat.auto_login(hotReload=True, enableCmdQR=2)

positiveSendingThread = threading.Thread(target=send_online_notification,
    args=('ether',))
positiveSendingThread.setDaemon(True)
positiveSendingThread.start()

itchat.run()
