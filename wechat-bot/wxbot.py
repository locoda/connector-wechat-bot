# -*- coding: utf-8 -*-

from wxpy import *
from messages import *

import unicodedata
import re
import time
import logging

logging.basicConfig()
bot = Bot(cache_path=True, console_qr=True,)
bot.enable_puid()

@bot.register(bot.self, except_self=False)
def reply(msg):
	if msg.text == '1':
		return 'I\'m Still Alive!! ' + time.strftime('%y/%m/%d-%H:%M:%S', time.localtime())
	else:
		return tuling_reply(content, msg.sender.puid)

@bot.register(Group, TEXT)
def group_msg(msg):
	if msg.is_at:
		content = re.sub('@[^\s]*', '', unicodedata.normalize('NFKC', msg.text)).strip()



		try:
			msg.reply(apiai_reply(content, msg.member.puid))
		except Exception as error:
			print error
			msg.reply(tuling_reply(content, msg.member.puid))


embed()
