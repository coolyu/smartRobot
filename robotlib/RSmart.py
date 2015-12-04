# -*- coding: utf-8 -*-
import requests
import os
import time
import logging
import traceback


class RSmart:
    def __init__(self):
        self.PATH = "%s%stmp%s" % (os.getcwd(), os.sep,os.sep)
        self.RES_PATH = "%s%sresources%s" % (os.getcwd(), os.sep,os.sep)
        self.Last_Sound = ""
        self.loger = logging.getLogger("RSmart")
        self.BAIDU_API_Key = "llAzbbYrDx6Zttd3Ga7hq2op"
        self.BAIDU_SECRET_KEY = "38406ec2d68dd50162d8b39f03a317ff"
        self.TULING_API_KEY = "db182e5c305492e330e643c3753c97ee"
        self.log = logging.getLogger('RSmart')

    def remove_tmpfile(self):
        for eachFile in os.listdir(self.PATH):
            if os.path.isfile(self.PATH +"/"+eachFile) & eachFile.endswith(".mp3"):
                ft = os.stat(self.PATH+"/"+eachFile);
                ltime = int(ft.st_mtime); #获取文件最后修改时间
                ntime = int(time.time())-120; #获取现在时间减去2分钟
                if ltime<=ntime :
                    os.remove(self.PATH+"/"+eachFile);


    def get_baidu_token(self):
        needrequest = False
        filename = self.PATH + 'token.txt'
        if os.path.isfile(filename):
            diff = os.stat(filename).st_ctime - time.time()
            if diff > 80000:
                needrequest = True
            else:
                with open(filename,"rt") as f:
                    token = f.readline()
                    return token
        else:
            needrequest = True

        tk = ""
        if needrequest:
            url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s'% (self.BAIDU_API_Key,self.BAIDU_SECRET_KEY)
            while True:
                req = requests.get(url,verify=False)
                # certpath = "%sbaidu.pem" % self.RES_PATH
                # self.log.debug(certpath)
                #req = requests.get(url , cert = certpath  )
                if req.status_code == requests.codes.ok:
                    token = req.json()
                    with open(filename,"w") as f:
                        f.write(token['access_token'])
                    tk = token['access_token']
                    break
            return tk

    def sound2txt(self,filename):
        length = os.path.getsize(filename)
        headers = {'Content-Type':'audio/pcm;rate=16000','Content-length': length}
        token = self.get_baidu_token()
        url = "http://vop.baidu.com/server_api?lan=zh&cuid=COOLYU_SMART_ROBOT&token=%s" % token
        try:
            with open(filename,"rb") as f:
                r = requests.post(url,data=f,headers=headers)
                if r.json()['err_no'] == 0:
                    return r.json()['result'][0]
                else:
                    self.loger.error("Error From :Sound2TXT , %s : %s" % (r.json()['err_no'], r.json()['err_msg']))
                    return ""
        except Exception , e:
            traceback.print_stack()
            self.log.error( "%s is Error : %s " % ( "sound2txt" , e.message))
            return ""

    def txt2sound(self,volstr):
        #self.log.debug(len(volstr))
        data = {
        "tex":volstr,
        "lan":"zh",
        "ctp":1,
        "tok":self.get_baidu_token(),
        "cuid":"COOLYU_SMART_ROBOT",
        "spd":6,
        "pit":5,
        "vol":5,
        "per":1}
        url = "http://tsn.baidu.com/text2audio"
        self.log.debug(self.Last_Sound)
        try:
            # if (os.path.exists(self.Last_Sound)) & (self.Last_Sound.find(self.PATH) > -1):
            #     os.remove(self.Last_Sound)
            r = requests.post(url,data)
            self.log.debug(r.headers)

            if r.headers["Content-Type"] == 'audio/mp3':
                self.Last_Sound = self.PATH + "replyvol" + time.strftime('%Y%m%d_%H%M%S') + '.mp3'
                f = open(self.Last_Sound,"wb")
                f.write(r.content)
                f.close()
                return self.Last_Sound
            else:
                traceback.print_stack()
                self.log.error(r.content)
                return "%sagain.mp3" % self.RES_PATH
        except Exception , e:
            self.log.error( "%s is Error : %s " % ( "txt2sound" , e.message))
            traceback.print_stack()
            return "%sagain.mp3" % self.RES_PATH

    def serchresult(self,info):
        methods = {
                100000:self.__process100000, #text
                200000:self.__process200000, #image
                302000:self.__process302000, #news
                305000:self.__process305000, #train
                306000:self.__process306000, #fly
                }
        if len(info.strip()) > 1:
            url = "http://www.tuling123.com/openapi/api?userid=COOLYU_SMART_ROBOT&key=%s&info=%s" % (self.TULING_API_KEY ,info )
            try:
                req = requests.get(url)
                js = req.json()
                key = js['code']
                self.log.debug(js)
                if( (key in methods.keys()) ):
                    return methods[key](js)
                else:
                    return "有些问题我暂时无法解答，让时间把我变得更加聪明的时候再说吧"
            except Exception , e:
                self.log.error( "%s is Error : %s " % ( "serchresult" , e.message))
                return "有些问题我暂时无法解答，让时间把我变得更加聪明的时候再说吧"
        else:
            return "再多说一点吧,在强大的内心也需要热情的表达"

    def __process100000(self,js):
        return js['text']

    def __process200000(self,js):
        return "您找的是图片么？我现在无法展示给您看"

    def __process302000(self,js):
        text = js['text']
        num = 0
        for x in js['list']:
            text += "。" + x['article']
            num +=1
            if num > 2:
                break;
        return text

    def __process305000(self,js):
        text = js['text']
        num = 0
        for x in js['list']:
            text += "。车次" + x['trainnum'] +  ',始发站：' + x['start'] + ',终点站:' + x['terminal'] + ',发车时间:' + x['starttime']
            num +=1
            if num > 2:
                break;
        return text

    def __process306000(self,js):
        text = js['text']
        num = 0
        for x in js['list']:
            text += "。航班号" + x['flight'] + ',起飞时间:' + x['starttime']
            num +=1
            if num > 2:
                break;
        return text