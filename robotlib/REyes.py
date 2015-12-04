# -*- coding: utf-8 -*-
import pygame
import pygame.camera
import os
import requests
import time
import cv2
import logging
import numpy as np
import traceback

class REyes:
    def __init__(self):
        self.PATH = "%s%stmp%s" % (os.getcwd(), os.sep,os.sep)
        self.RES_PATH = "%s%shaarcascades%s" % (os.getcwd(), os.sep,os.sep)
        self.IMAGE_WIIDTH = 1024
        self.IMAGE_HEIGHT = 768
        self.DEVICE_NAME = "/dev/video0"
        self.FACE_APIKey = "d3903cd76f71f9bafb6b35fa41d6cda1"
        self.FACE_Secret = "ht5sH1INyKm39mI3u2RZITIvCWltJAXD"
        self.FACE_APIURL = "http://apicn.faceplusplus.com"
        self.Image_Name = "%scarema.jpg" % self.PATH
        self.log = logging.getLogger('REyes')
        self.cap = None

    def __see(self):# old function , new is __findface
        pygame.init()
        pygame.camera.init()
        cam = pygame.camera.Camera(self.DEVICE_NAME,(self.IMAGE_WIIDTH,self.IMAGE_HEIGHT),"RGB")
        self.Image_Name = '%s%s.jpg' % (self.PATH,time.strftime('%Y%m%d_%H%M%S'))
        cam.start()
        img = cam.get_image()
        pygame.image.save(img,self.Image_Name)
        cam.stop()
        pygame.camera.quit()
        #pygame.quit()

    def beginCapture(self):
        if self.cap == None:
            self.cap = cv2.VideoCapture(0)

    def endCapture(self):
        if self.cap != None:
            self.log.info("cam release")
            self.cap.release()

    def FindFace(self):
        success,frame=self.cap.read()
        classifier=cv2.CascadeClassifier("%shaarcascade_frontalface_default.xml" % self.RES_PATH)
        if success:
            size=frame.shape[:2]
            # self.Image_Name = '%s%s.jpg' % (self.PATH,time.strftime('%Y%m%d_%H%M%S'))
            # cv2.imwrite(self.Image_Name,frame)
            image=np.zeros(size,dtype=np.float16)
            image=cv2.cvtColor(frame,cv2.cv.CV_BGR2GRAY)
            cv2.equalizeHist(image,image)
            divisor=8
            h,w=size
            minSize=(w/divisor,h/divisor)
            faceRects=classifier.detectMultiScale(image,1.2,2,cv2.CASCADE_SCALE_IMAGE,minSize)
            self.log.info("找到 %d 个面部特征" % len(faceRects))
            if len(faceRects) > 0:
                self.Image_Name = '%s%s.jpg' % (self.PATH,time.strftime('%Y%m%d_%H%M%S'))
                cv2.imwrite(self.Image_Name,frame)
                return True
            else:
                return False
        else:
            traceback.print_stack()
            self.log.error("摄像头读取错误")
            return False

    def __detect(self):
        length = os.path.getsize(self.Image_Name)
        url = "%s/v2/detection/detect?api_key=%s&api_secret=%s&mode=oneface&attribute=glass,pose,gender,age,race,smiling" % (self.FACE_APIURL , self.FACE_APIKey , self.FACE_Secret)
        with open(self.Image_Name,"rb") as f:
            r = requests.post(url,files={"img":f})
            if r.status_code == requests.codes.ok:
                res = r.json()
                if len(res['face']) > 0:
                    Man = {
                        'gender': res['face'][0]['attribute']['gender']['value'],
                        'age_min':  res['face'][0]['attribute']['age']['value'] - res['face'][0]['attribute']['age']['range'],
                        'age_max':  res['face'][0]['attribute']['age']['value'] + res['face'][0]['attribute']['age']['range'],
                        'smiling': res['face'][0]['attribute']['smiling']['value']
                    }
                else:
                    Man = {
                        'gender': 'NONE',
                        'age_min': 0,
                        'age_max': 100,
                        'smiling': 0
                    }
                return Man
            else:
                Man = {
                        'gender': 'NONE',
                        'age_min': 0,
                        'age_max': 100,
                        'smiling': 0
                    }
                return Man



    def See(self):
        try:
            man =  self.__detect()
            #os.remove(self.Image_Name)
            return man
        except:
            Man = {
                    'gender': 'NONE',
                    'age_min': 0,
                    'age_max': 100,
                    'smiling': 0
                }
            return  Man


