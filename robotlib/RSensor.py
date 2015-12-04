# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO         ## Import GPIO Library
import time			## Import 'time' library (for 'sleep')
import logging


class RSensor:

    def __init__(self):
        self.Induction_PIN = 0
        self.Distinct_Trig_PIN = 0
        self.Distinct_Echo_PIN = 0
        self.Switch_PIN = 0
        self.log = logging.getLogger('RSensor')

    def init(self,DictPin):
        if isinstance(DictPin,dict):
            GPIO.setmode(GPIO.BOARD)
            methods = {
                'Switch':self.__setSwitchPIN, #text
                'Induction':self.__setInductionPIN, #image
                'DistinctTrig':self.__setDistinctTrigPIN, #news
                'DistinctEcho':self.__setDistinctEchoPIN, #train
                }
            for key in DictPin:
                if (key in methods.keys()):
                     methods[key](DictPin[key])
            self.log.debug("sw %s in %s trig %s echo %s" % (self.Switch_PIN,self.Induction_PIN,self.Distinct_Trig_PIN , self.Distinct_Echo_PIN))
            if self.Distinct_Echo_PIN * self.Distinct_Trig_PIN * self.Induction_PIN * self.Switch_PIN == 0:
                self.log.error("有部分管脚没有进行设置")
                return False
            else:
                return True
        else:
            self.log.error("输入管脚应为字典类型")
            return False

    def allowStart(self):
        return not GPIO.input(self.Switch_PIN)

    def waitForMove(self):
        while True:
            if self.allowStart():
                while GPIO.input(self.Induction_PIN):
                    return True;
            else:
                self.log.info("等待开始按钮按下")
                time.sleep(1)

    def getDistinct(self):
        try:
            if self.allowStart():
                dict = self.__Distinct(5)
                return dict
            else:
                logging.debug("开启我吧")
                return  -1.0
        except Exception , e:
            self.log.error( "%s is Error : %s " % ( "RSensor::RUN" , e.message))
            return -1.0


    def __setSwitchPIN(self,PIN):
        self.Switch_PIN = PIN
        GPIO.setup(self.Switch_PIN,GPIO.IN)

    def __setInductionPIN(self,pin):
        self.Induction_PIN = pin
        GPIO.setup(self.Induction_PIN , GPIO.IN)


    def __setDistinctTrigPIN(self,pin):
        self.Distinct_Trig_PIN = pin
        GPIO.setup(self.Distinct_Trig_PIN,GPIO.OUT,initial=GPIO.LOW)


    def __setDistinctEchoPIN(self,pin):
        self.Distinct_Echo_PIN = pin
        GPIO.setup(self.Distinct_Echo_PIN,GPIO.IN)


    def __DistinctOnce(self):
        GPIO.output(self.Distinct_Trig_PIN,GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(self.Distinct_Trig_PIN,GPIO.LOW)
        tmend = time.time() + 5
        noInput = False
        while GPIO.input(self.Distinct_Echo_PIN) == False :
            if time.time() < tmend:
                pass
            else:
                noInput = True
                break
        if noInput == False:
            t1 = time.time()
            while GPIO.input(self.Distinct_Echo_PIN):
                pass
            t2 = time.time()
            return (t2-t1)*340/2
        else:
            return -1.0

    def __Distinct(self,maxnum):
        num = 0
        sum = 0.0
        while num <= maxnum:
            num += 1
            dic =  self.__DistinctOnce()
            #self.log.debug("dist is %s" % dic)
            if dic > -1:
                sum += dic;
            else:
                self.log.debug("Distinct Sennsor is Error")
                raise Exception("Distinct Sennsor is Error")
        return  (sum / (num + 1))

