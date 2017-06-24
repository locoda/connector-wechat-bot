# -*- coding: utf-8 -*-

import io
import requests
from lxml import etree
import json
import random
import apiai

from api_tokens import *

def tuling_reply(msg_content, user_id):
    url_api = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : TULING_TOKEN,
        'info'   : msg_content,
        'userid' : user_id,
    }
    
    print "use Tuling reply"
    s = requests.post(url_api, data=data).json()
    print 'return code: ' + str(s['code'])
    if s['code'] == 100000:
		return s['text']
    if s['code'] == 200000:
        return s['text'] + s['url']
    if s['code'] == 302000:
        news = random.choice(s['list'])
        return news['article'] + '\n' + news['detailurl']
    if s['code'] == 308000:
        menu = random.choice(s['list'])
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
        raise Exception('api.ai cannot reply this message')
    if s['status']['code'] == 200:
        print "use APIAI reply"
        print 'return code: ' + str(s['status']['code'])
        return s['result']['fulfillment']['speech']


def emotions_reply(keyword):
    print "try gif reply..."
    res = requests.get('https://www.doutula.com/search', {'keyword': keyword})
    html = etree.HTML(res.text)
    url = 'http:' + random.choice(html.xpath('//div[@class="image-container"][1]//img[contains(@class, "img-responsive")]/@data-original'))

    return url
