# -*- coding: utf-8 -*-
import time			## Import 'time' library (for 'sleep')
import logging

class RRsensorTest:
    def Near(self):
        time.sleep(5)
        logging.getLogger("Sensor").info("有人来了")
        return True

    def init(self,DictPin):
        pass

    def getDistinct(self):
        return 5.0

    def waitForMov(self):
        return  True