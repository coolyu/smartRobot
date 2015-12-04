# -*- coding: utf-8 -*-
__author__ = 'Coolyu'

import robotlib as rb
import time
import os
import logging,coloredlogs
import pygame
import RPi.GPIO as GPIO
import traceback

logging.basicConfig(level = logging.INFO, filemode = 'w', format = '%(asctime)s - %(levelname)s:[%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s')
# logging.addLevelName( logging.INFO, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.INFO))
# logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
coloredlogs.install()
log = logging.getLogger("main")

sm = rb.RSmart()
rs = rb.RSound()
rp = rb.RReply()
sn = rb.RSensor()
re = rb.REyes()

def initSensor():
    dict = {
            'Switch': 11,
            'Induction' : 37,
            'DistinctTrig': 35,
            'DistinctEcho' : 33
            }
    return sn.init(dict)


def BrainProcess():
    sm.remove_tmpfile() # remove tmpfile
    path = "%s%stmp%s" % (os.getcwd(), os.sep,os.sep)
    filename = path + "vol.wav"

    beg = time.time()
    log.info("开始录制声音" )
    rs.record_to_file(filename)
    log.info("录制结束,保存到 :%s , 耗时 %0.2f s" % (filename , time.time() - beg))

    if os.path.getsize(filename) > 0:
        beg = time.time()
        log.info("将声音转换为文字")
        text = rp.processAsk( sm.sound2txt(filename) )
        log.info("转换成功,您说的是:%s , 耗时 : %0.2f s" % ( text , time.time() - beg))

        beg = time.time()
        log.info("开始寻找答案")
        if text == "":
            ret = "我没有听清楚，请您重新和我说一次好么"
        else:
            ret = rp.processReplay( sm.serchresult( text ) )
        log.info("找到答案为 :%s ,耗时 : %0.2f s" % (ret,time.time() - beg))

        beg = time.time()
        log.info("将答案转化为声音")
        mkvol = sm.txt2sound(ret)
        log.info("转换声音完毕,保存在 :%s , 耗时 %0.2f s" % (mkvol ,time.time() - beg))

        beg = time.time()
        log.info("回答您的提问")
        rs.playsound(mkvol)
        log.info("回答完毕,耗时 %0.2f s" % (time.time() - beg))
        return True
    else:
        log.info("没人说话,那我去休息了")
        return False

def BeginSay(man):

    log.info("来者性别别 %s 年龄在 %d 到 %d 之间，笑容指数 %f" % (man['gender'] ,man['age_min'],man['age_max'],man['smiling'] ))
    rs.playsound( "%shello.mp3" % resourcespath )
    if man['gender'] == "Male":
        rs.playsound( "%ssir.mp3" % resourcespath )
    elif man['gender'] == "Female":
        rs.playsound( "%smiss.mp3" % resourcespath )

    if man['smiling'] > 50:
        rs.playsound( "%sxinqing.mp3" % resourcespath )
        rs.playsound( "%shappy.mp3" % resourcespath )

    rs.playsound( "%shelp.mp3" % resourcespath )


if __name__ == '__main__':

    if initSensor() == False:
        log.error("感应器定义失败")
        exit()
    resourcespath = "%s%sresources%s" % (os.getcwd(), os.sep,os.sep)
    log.info("系统启动")
    sm.remove_tmpfile()
    sm.get_baidu_token()
    try:
        re.beginCapture()
        while True:
            if sn.waitForMove():
                n = sn.getDistinct()
                log.debug("n is %d" % n )
                while n > 0.00005:
                    if re.FindFace():
                        break
                    time.sleep(0.5)
                    n = sn.getDistinct()
                    log.info("距离我 %f 米" % n)
                man = re.See()
                BeginSay(man)
                while BrainProcess():
                    pass
            time.sleep(5)
        re.endCapture()
    except KeyboardInterrupt:
        pygame.mixer.stop()
        pygame.quit()
        GPIO.cleanup()
        re.endCapture()
    except Exception , e:
        #traceback.print_stack()
        log.error( ("%s is Error : %s " % ("Main",e.message)) )
        pygame.mixer.stop()
        pygame.quit()
        GPIO.cleanup()
