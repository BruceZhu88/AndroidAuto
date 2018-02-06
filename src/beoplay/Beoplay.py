"""
Created on 2018-01-10
# -*- coding: utf-8 -*-
"""

import math
import os
from time import sleep
from src.common.Logger import Logger
from src.common.app import App

log = Logger("main").logger()


class Beoplay(App):

    @classmethod
    def click_allow(cls):
        cls.find_ele('id', 15, 'com.android.packageinstaller:id/permission_allow_button').click()

    @classmethod
    def search_sample(cls, name):
        log.info('Searching {}...'.format(name))
        for i in range(1, 5):
            for j in range(1, 5):  # check 3 times
                try:
                    dut_name = cls.find_ele('ui', 15, 'new UiSelector().text("{}")'.format(name))
                    if dut_name is not None:
                        log.info('Found {}'.format(name))
                        dut_name.click()
                        log.info('Connecting with {}'.format(name))
                        return True
                except Exception as e:
                    log.info(e)
            log.info('Swipe screen to find sample')
            cls.swipe('up', 200)
            sleep(1)
        log.info('Can not find {}'.format(name))
        return False

    @classmethod
    def play_audio(cls, phone):
        element = cls.driver.find_elements_by_class_name(
            "android.widget.ImageView")[6]

        if Beoplay.test_same_as(phone, "NOW_PLAYING\pause", element):
            # [3]TWS [4]Tonetouch [5]Previous track [6]Play/Pause [7]Next track
            element.click()
            sleep(5)
            if Beoplay.test_same_as(phone, "NOW_PLAYING\play", element):

                log.info('--play button is ok')
                return True
            else:
                log.info('--play button is incorrect')
                element.click()
                Beoplay.click_key(4)
                return False

    @classmethod
    def pause_audio(cls, phone):
        element = cls.driver.find_elements_by_class_name(
            "android.widget.ImageView")[6]

        if Beoplay.test_same_as(phone, "NOW_PLAYING\play", element):
            # [3]TWS [4]Tonetouch [5]Previous track [6]Play/Pause [7]Next track
            element.click()
            sleep(5)
            if Beoplay.test_same_as(phone, "NOW_PLAYING\pause", element):
                log.info('--pause button is ok')
                return True
            else:
                log.info('--pause button is incorrect')
                Beoplay.click_key(4)
                return False

    @classmethod
    def change_color(cls, num):  # Precondition: must stay on SETTING PAGE
        cls.driver.find_elements_by_id(
            'dk.shape.beoplay:id/color')[num].click()

    @classmethod
    def check_sample(cls, name, phone):
        """
        check sample is on or off, and which source
        """
        for i in range(1, 8):  # use return over, not break
            try:
                dut_name = cls.driver.find_element_by_android_uiautomator(
                    'new UiSelector().text("%s")' % name)
                if dut_name:
                    element = cls.driver.find_elements_by_class_name(
                        "android.widget.ImageView")[1]
                    log.info('--DUT is power on')
                    '''
                    if Beoplay.find_text('Bluetooth') & Beoplay.test_same_as(phone,'Bluetooth', element):  #different phone,picture size different
                        log.info('Debug message') --DUT connect with Bluetooth'
                    elif Beoplay.find_text('Aux In') & Beoplay.test_same_as(phone,'Aux In', element):
                        log.info('Debug message') --DUT connect with Aux In'  
                    elif Beoplay.find_text('USB') & Beoplay.test_same_as(phone,'USB', element):
                        log.info('Debug message') --DUT connect with USB' 
                    else:
                        log.info('Debug message')No source connect'   
                    '''
                    return True
            except Exception as e:
                log.info(e)
                sleep(3)
                log.info('check sample %d times' % i)
        log.info('--Abnormal shutdown on DUT')
        log.info('*****Maybe here has some issue, test stop!')
        log.info('*****Back to \'MY PRODUCTS\' page')
        Beoplay.click_key(4)
        return False

    @classmethod
    def check_name(cls, cn):  # before name and change name
        for i in range(1, 3):
            try:
                dut_name = cls.driver.find_element_by_android_uiautomator(
                    'new UiSelector().text("%s")' % cn)
                if dut_name:
                    return True
            except Exception as e:
                log.info(e)
                log.info('Can not find the changed name %s' % cn)
                return False

    @classmethod
    def check_color(cls, phone, num):  # before name and change name
        element = cls.driver.find_elements_by_class_name(
            "android.widget.ImageView")[2]
        if Beoplay.test_same_as(phone, num, element):
            log.info('color is ok')
            return True
        else:
            log.info('color is incorrect')
            return False

    @classmethod
    def change_name(cls, name):
        # Go to setting Page
        Beoplay.click_setting()
        dutName = cls.driver.find_element_by_class_name(
            'android.widget.EditText')
        dutName = dutName.get_attribute("text")
        log.info('--The current DUT name is ' + dutName)
        Beoplay.click_sample(dutName)
        # Delete current name
        cls.driver.find_element_by_class_name(
            'android.widget.EditText').clear()
        '''
        cls.driver.keyevent(123)    #delete key  
        for i in range(0,len(dutName)):
            cls.driver.keyevent(67)       
        sleep(1)
        '''
        # change DUT name
        textfields = cls.driver.find_elements_by_class_name(
            "android.widget.EditText")
        textfields[0].send_keys(name)  # how to send character string
        sleep(0.5)
        cls.driver.keyevent(4)  # back key

    @classmethod
    def change_volumn(cls, orientation):  # up or down
        # action = webdriver.webdriver.TouchAction(cls)
        element = cls.driver.find_elements_by_class_name("android.view.View")[
            2]
        location = element.location
        size = element.size
        # box = (location["x"], location["y"], location["x"] + size["width"], location["y"] + size["height"])
        r = size["width"] / 2
        x0 = location["x"] + size["width"] / 2
        y0 = location["y"] + size["height"] / 2
        x = 0
        y = 0
        # log.info('r=%d,x=%d,y=%d'%(r,x0,y0))
        # log.info('start' )
        if orientation == 'up':
            n = 3.1415926 * 6 / 4  # from 240  -3.1415926*1/2, 3.1415926*6/4
            n1 = -3.1415926 * 1 / 2
            while (n >= n1):
                x = x0 + r * math.cos(n)
                y = y0 - r * math.sin(n)
                cls.driver.tap([(x - 1, y - 1), (x + 1, y + 1)])
                # log.info(x=%d,y=%d'%(x,y))
                n = n - 0.05
        elif orientation == 'down':
            n = -3.1415926 * 1 / 2  # from 240  -3.1415926*1/2, 3.1415926*6/4
            n1 = 3.1415926 * 6 / 4
            while (n <= n1 + 0.15):
                x = x0 + r * math.cos(n)
                y = y0 - r * math.sin(n)
                cls.driver.tap([(x - 1, y - 1), (x + 1, y + 1)])
                # log.info('x=%d,y=%d'%(x,y))
                n = n + 0.05
        else:
            log.info('Parameter error')
            return
        '''
        while (n>=n1):
            x=x0+r*math.cos(n)
            y=y0-r*math.sin(n)
            #x1=x0
            #y1=y0
            #action.press(x0, y0).moveTo(x, y).release().perform()
            #cls.driver.swipe(x1, y1, x , y) 
            cls.driver.tap([(x-1, y-1),(x+1, y+1)])
            log.info('Debug message')x=%d,y=%d'%(x,y)
            n=n-0.05
         '''

    @classmethod
    def test_get_screen_by_element(cls):
        """
                Speaker icon and color
        """
        '''
        element = cls.driver.find_elements_by_class_name("android.view.View")[2]
        cls.extend.get_screenshot_by_element(element).write_to_file("D:\\Bruce\\screen", "Tonetouch2")  

        element = cls.driver.find_elements_by_class_name("android.view.View")[3]
        cls.extend.get_screenshot_by_element(element).write_to_file("D:\\Bruce\\screen", "Tonetouch3")                
        '''
        sleep(4)
        for i in range(0, 10):
            log.info('ok')
            try:
                sleep(1)
                Beoplay.click_setting()
                sleep(1.5)
                cls.driver.find_elements_by_id(
                    'dk.shape.beoplay:id/color')[i].click()
                Beoplay.click_save()
                sleep(3)
                element = cls.driver.find_elements_by_class_name(
                    "android.widget.ImageView")[2]
                cls.extend.get_screenshot_by_element(
                    element).write_to_file("D:\\Bruce\\screen", "%s" % i)
            except:
                log.info('over')
                return

        '''
        Beoplay.click_sample('123')
        sleep(4)
        element = cls.driver.find_elements_by_class_name("android.widget.ImageView")[6]
        cls.extend.get_screenshot_by_element(element).write_to_file("D:\\Bruce\\screen", "pause") 
        print "pause"
        sleep(7)
        
        element.click()
        print "play"
        sleep(7)
        element = cls.driver.find_elements_by_class_name("android.widget.ImageView")[6]
        cls.extend.get_screenshot_by_element(element).write_to_file("D:\\Bruce\\screen", "play") 
        
        print "Please connect DUT with Bluetooth"
        sleep(7)
        element = cls.driver.find_elements_by_class_name("android.widget.ImageView")[1]
        cls.extend.get_screenshot_by_element(element).write_to_file("D:\\Bruce\\screen", "Bluetooth")     
        
        print "Please connect DUT with AUX"
        sleep(7)        
        element = cls.driver.find_elements_by_class_name("android.widget.ImageView")[1]
        cls.extend.get_screenshot_by_element(element).write_to_file("D:\\Bruce\\screen", "Aux In")     
        
        print "Please connect DUT with USB"
        sleep(7)          
        element = cls.driver.find_elements_by_class_name("android.widget.ImageView")[1]
        cls.extend.get_screenshot_by_element(element).write_to_file("D:\\Bruce\\screen", "USB")          
              
        #cls.assertTrue(os.path.isfile("D:\\Bruce\\screen\\image.png"))  
        '''

    @classmethod
    def test_same_as(cls, phone, path, element):
        cls.screen_path = os.path.realpath(
            os.path.join(os.getcwd(), "..", 'screen'))

        # element = cls.driver.find_elements_by_class_name("android.widget.ImageView")[6]
        load = cls.extend.load_image(
            "%s\\%s\\%s.png" % (cls.screen_path, phone, path))
        result = cls.extend.get_screenshot_by_element(
            element).same_as(load, 0)
        return result
        # cls.assertTrue(result)

    '''

    @classmethod
    def case1_change_name_color(cls):
        i = 0
        f = open("D:\TestData\data_name.ini","r")     # cant't identify "(" ")"
        line = f.readline()     
        while line:      
            log.info('Debug message')-----------------------------------------------------------'              
            print "this is the %d times" % (i + 1)
            log.info('Debug message')  --Change DUT name to %s'%line
            sleep(0.5)
            Beoplay.change_name(line,i)
            i = i + 1
            line = f.readline()
        f.close()  
        log.info('Debug message')----------------Test over'                 
    '''
