#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import time
from datetime import datetime

import math
import cv2
import numpy as np

time_cycle = 80


class MyAlgorithm(threading.Thread):

    def __init__(self, camera, motors):
        self.camera = camera
        self.motors = motors
        self.threshold_image = np.zeros((640, 360, 3), np.uint8)
        self.color_image = np.zeros((640, 360, 3), np.uint8)
        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        self.threshold_image_lock = threading.Lock()
        self.color_image_lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)

    def getImage(self):
        self.lock.acquire()
        img = self.camera.getImage().data
        self.lock.release()
        return img

    def set_color_image(self, image):
        img = np.copy(image)
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        self.color_image_lock.acquire()
        self.color_image = img
        self.color_image_lock.release()

    def get_color_image(self):
        self.color_image_lock.acquire()
        img = np.copy(self.color_image)
        self.color_image_lock.release()
        return img

    def set_threshold_image(self, image):
        # img = np.copy(image)
        # if len(img.shape) == 2:
        # img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        self.threshold_image_lock.acquire()
        height,width,channels = image.shape
        descentre = 100
        rows = 100
        img2 = image[int((height/2))+descentre:int((height)/2)+(descentre+rows)][1:width]
        img3 = cv2.cvtColor(img2,cv2.COLOR_BGR2HSV)
        high = np.array([120,255,255])
        low = np.array([70,20,20])
        mask = cv2.inRange(img3,low,high)
        img4 = cv2.bitwise_and(img3,img3,mask=mask)
        m = cv2.moments(mask,False)
        try:
            cx,cy = m['m10']/m['m00'] ,m['m01']/m['m00']
        except ZeroDivisionError:
            cx,cy = height/2,width/2
        cv2.circle(img4,(int(cx),int(cy)),10,(0,255,255),-1)
        
        error_x=cx-width/2
        self.motors.sendV(4)
        self.motors.sendW(-error_x/100)
        self.threshold_image = img4
        self.threshold_image_lock.release()

    def get_threshold_image(self):
        self.threshold_image_lock.acquire()
        img = np.copy(self.threshold_image)
        self.threshold_image_lock.release()
        return img

    def run(self):

        while (not self.kill_event.is_set()):
            start_time = datetime.now()
            if not self.stop_event.is_set():
                self.algorithm()
            finish_Time = datetime.now()
            dt = finish_Time - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * \
                1000 + dt.microseconds / 1000.0
            #print (ms)
            if (ms < time_cycle):
                time.sleep((time_cycle - ms) / 1000.0)

    def stop(self):
        self.stop_event.set()

    def play(self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill(self):
        self.kill_event.set()

    def algorithm(self):
        # GETTING THE IMAGES
        image = self.getImage()

        # Add your code here
        print("Runing")


        # EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        # self.motors.sendV(10)
        # self.motors.sendW(5)

        # SHOW THE FILTERED IMAGE ON THE GUI
        self.set_threshold_image(image)
