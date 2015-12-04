# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO         ## Import GPIO Library
import time			## Import 'time' library (for 'sleep')
import logging

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG, filemode = 'w', format = '%(asctime)s - %(levelname)s: %(message)s')
    log = logging.getLogger("main")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(37, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    #GPIO.setup(37, GPIO.IN)
try:
    while GPIO.wait_for_edge(37,GPIO.RISING):
        value = GPIO.input(11)
        if value == False:
            log.debug( "run here")
            while GPIO.wait_for_edge(37,GPIO.RISING):
                log.debug( "move")
                break
        time.sleep(1)
    print("over")
except Exception , e:
    log.debug( "%s is Error : %s " ( "testgpio" , e.message))
    pass
finally:
     GPIO.cleanup()

