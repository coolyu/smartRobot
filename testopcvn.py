# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
cv2.namedWindow("test")
cap=cv2.VideoCapture(0)
success,frame=cap.read()
classifier=cv2.CascadeClassifier("d:\\python\\haarcascades\\haarcascade_frontalface_alt.xml")   #确保此xml文件与该py文件在一个文件夹下，否则将这里改为绝对路径，此xml文件可在D:\My Documents\Downloads\opencv\sources\data\haarcascades下找到。

while success:
    success,frame=cap.read()
    size=frame.shape[:2]
    image=np.zeros(size,dtype=np.float16)
    image=cv2.cvtColor(frame,cv2.cv.CV_BGR2GRAY)
    cv2.equalizeHist(image,image)
    divisor=8
    h,w=size
    minSize=(w/divisor,h/divisor)
    faceRects=classifier.detectMultiScale(image,1.2,2,cv2.CASCADE_SCALE_IMAGE,minSize)
    print(len(faceRects))
    if len(faceRects)>0:
        for faceRect in faceRects:
            x,y,w,h=faceRect
            cv2.circle(frame,(x+w/2,y+h/2),min(w/2,h/2),(255,0,0),2)
            # cv2.circle(frame,(x+w/4,y+h/4),min(w/8,h/8),(255,0,0))
            # cv2.circle(frame,(x+3*w/4,y+h/4),min(w/8,h/8),(255,0,0))
            cv2.rectangle(frame,(x+3*w/8,y+3*h/4),(x+5*w/8,y+7*h/8),(255,0,0))
        cv2.imshow("test",frame)
        key=cv2.waitKey(10)
        c=chr(key&255)
        if c in ['q','Q',chr(27)]:
            break

cv2.destroyWindow("test")