# -*- coding: utf-8 -*-
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class RReply:
    def __init__(self):
        pass

    def processAsk(self,ask):
        text = ask
        if text.find('天气') > -1:
            text = "大连" + ask
        return text

    def processReplay(self,replay):
        dr = re.compile(r'<[^>]+>',re.S)
        text = dr.sub('',replay)
        p = re.compile(r'(\d{1,2})/(\d{1,2})') #11/08
        text = p.sub(r'\1月\2日',text)
        return text