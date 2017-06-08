# coding=utf8
import itchat
from itchat.content import *

import unicodedata
import requests
import json
from bs4 import BeautifulSoup

import os
import io
import hashlib
import random
import time
import threading

import apiai
#from google import google

from api_tokens import APIAI_TOKEN, TULING_TOKEN

def send_online_notification(name):
    memberList = itchat.search_friends(name = name)
    
    while True:
        for member in memberList:
            itchat.send('I\'m Still Alive!! ' + time.strftime(
                '%y/%m/%d-%H:%M:%S', time.localtime()), member['UserName'])
            time.sleep(.5)
        time.sleep(1800)

# thanks: https://github.com/qwIvan/microMsg-bot/blob/master/meme.py
def search_gif(keyword):
    resp = requests.get('https://www.doutula.com/search', {'keyword': keyword})
    soup = BeautifulSoup(resp.text, 'lxml')
    return [('http:' + i.get('data-original'), 'http:' + i.get('data-backup')[:-4]) for i in soup.select('.select-container img') if i.get('class') != ['gif']]

def gif_reply(keyword, user_id):
    print "try gif reply..."
    imgs = search_gif(keyword)

    if not imgs:
	   # print apiai_reply(keyword, user_id)
        return 1, u'没有找到表情呢/(ㄒoㄒ)/~ 机器人来回答你：\n\n' + apiai_reply(keyword, user_id)

    print "use gif reply"
    img = random.choice(imgs)

    url = img[0]
    r = requests.get(url, stream=True)
    imageStorage = io.BytesIO()
    for block in r.iter_content(1024):
        imageStorage.write(block)
    imageStorage.seek(0)

    return 0, imageStorage


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
	# print s['text']
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
def TEXT_reply(msg):
    if msg['Content'].lower().endswith('.gif') or msg['Content'].lower().endswith('.jpg') or msg['Content'].lower().endswith('.png'):
        code, r = gif_reply(msg['Content'][:-4], msg['FromUserName'])
        if code == 0:
            itchat.send_image(r, msg['FromUserName'])
        elif code == 1:
            itchat.send(r, msg['FromUserName'])
    elif msg['Content'] == '1':
        itchat.send('I\'m Still Alive!! ' + time.strftime(
                '%y/%m/%d-%H:%M:%S', time.localtime()), msg['FromUserName'])
        time.sleep(.5)
    else:
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
        if info.lower().endswith('.gif') or info.lower().endswith('.jpg') or info.lower().endswith('.png'):
            code, r = gif_reply(info[:-4], userid)
            if code == 0:
                itchat.send_image(r, msg['FromUserName'])
            elif code == 1:
                itchat.send(r, msg['FromUserName'])
        else:
            itchat.send(apiai_reply(info, userid), msg['FromUserName'])


itchat.auto_login(hotReload=True, enableCmdQR=2)

os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

positiveSendingThread = threading.Thread(target=send_online_notification,
    args=('ether',))
positiveSendingThread.setDaemon(True)
positiveSendingThread.start()

itchat.run()
