# -*- coding: utf-8 -*-

from wxpy import *
from messages import *

import unicodedata
import re
import time
import logging
import threading
from tempfile import NamedTemporaryFile

logging.basicConfig()
bot = Bot(cache_path=True, console_qr=True)
bot.enable_puid()
extensions = ['.jpg', '.png', '.gif']

def send_online_notification(name):
	my_friend = ensure_one(bot.search(name))
	while True:
		my_friend.send('I\'m Still Alive!! ' + time.strftime('%y/%m/%d-%H:%M:%S', time.localtime()))
		time.sleep(3600)


@bot.register(bot.self)
def reply(msg):
	if msg.text == '1':
		return 'I\'m Still Alive!! ' + time.strftime('%y/%m/%d-%H:%M:%S', time.localtime())
	else:
		return tuling_reply(msg.text, msg.sender.puid)


@bot.register(Group, SYSTEM, except_self=False)
def incoming_student(msg):
	# print('haha')
	print(msg)
	print(msg.raw)
	# if u'加入' in msg.text:
	# 	msg.reply(tuling_reply('welcome'.encode('UTF-8'), msg.member.puid))
	# 	msg.reply_image('welcome.jpg')

@bot.register(Group, TEXT)
def group_msg(msg):
	if msg.is_at:
		content = re.sub('@[^\s]*', '', unicodedata.normalize('NFKC', msg.text)).strip()

		if content.endswith(tuple(extensions)):
			try:
				res = requests.get(emotions_reply(content[:-4]), allow_redirects=False)
				tmp = NamedTemporaryFile()
				tmp.write(res.content)
				tmp.flush()
				media_id = bot.upload_file(tmp.name)
				tmp.close()

				msg.reply_image('.gif', media_id=media_id)
			except Exception as error:
				print(error)
				msg.reply("本机器人没有找到相关表情~使用文字回复：\n" + tuling_reply(content, msg.member.puid))
		else:
			try:
				msg.reply(apiai_reply(content, msg.member.puid))
			except Exception as error:
				print(error)
				msg.reply(tuling_reply(content, msg.member.puid))

positiveSendingThread = threading.Thread(target=send_online_notification, args=('乙醚。',))
positiveSendingThread.setDaemon(True)
positiveSendingThread.start()

embed()
