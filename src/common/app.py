"""
Created on 2018-01-10
# -*- coding: utf-8 -*-
"""

from time import sleep
from appium import webdriver
# from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
# from src.common.AppiumScreenshot import ScreenShot
from src.common.Logger import Logger
from src.common.find_obj import coordinate

log = Logger("main").logger()


class App(object):
    @classmethod
    def connect(cls, **kwargs):
        assert len(kwargs) > 0
        desired_caps = {}
        desired_caps['platformName'] = kwargs.get('platformName')
        # desired_caps['version'] = '5.0.1'
        desired_caps['deviceName'] = kwargs.get('deviceName')
        # desired_caps['automationName'] = 'selendroid'
        desired_caps['newCommandTimeout'] = kwargs.get('timeout')
        desired_caps['appPackage'] = kwargs.get('appPackage')
        # '.app.splash.SplashActivity'
        desired_caps['appActivity'] = kwargs.get('appActivity')

        cls.driver = webdriver.Remote(
            kwargs['remote_server'], desired_caps)
        # waiting for the response of the appActivity
        sleep(2)
        # Back to Main Screen
        # cls.driver.press_keycode(3)

    @classmethod
    def current_activity(cls):
        activity = cls.driver.current_activity
        # print activity
        return activity

    @classmethod
    def start_activity(cls, package, activity):
        log.info('Starting activity {}'.format(activity))
        cls.driver.start_activity(package, activity)

    @classmethod
    def close(cls):
        sleep(5)
        cls.driver.close_app()

    @classmethod
    def close_and_launch_app(cls):
        log.info("Close app")
        cls.driver.close_app()
        sleep(5)
        log.info("Launch app")
        cls.driver.launch_app()

    @classmethod
    def quit(cls):
        cls.driver.quit()

    @classmethod
    def send_key(cls, value):
        cls.driver.keyevent(value)  # 4 back key

    @classmethod
    def find_ele(cls, ele_type, timeout, value):
        """
        Args:
            ele_type(str): element type
            timeout(int): max time at finding element
            value(str): element attribute value
        Returns:
            ele(WebElement): return object of found element
        """
        ele = None
        try:
            if ele_type == "id":
                WebDriverWait(cls.driver, timeout).until(
                    lambda driver: driver.find_element_by_id(value))
                ele = cls.driver.find_element_by_id(value)
            elif ele_type == "id_":
                WebDriverWait(cls.driver, timeout).until(
                    lambda driver: driver.find_elements_by_id(value))
                ele = cls.driver.find_elements_by_id(value)
            elif ele_type == "a_id":
                WebDriverWait(cls.driver, timeout).until(
                    lambda driver: driver.find_element_by_accessibility_id(value))
                ele = cls.driver.find_element_by_accessibility_id(value)
            elif ele_type == "ui":
                WebDriverWait(cls.driver, timeout).until(
                    lambda driver: driver.find_element_by_android_uiautomator(value))
                ele = cls.driver.find_element_by_android_uiautomator(value)
            elif ele_type == "class":
                WebDriverWait(cls.driver, timeout).until(
                    lambda driver: driver.find_element_by_class_name(value))
                ele = cls.driver.find_element_by_class_name(value)
            elif ele_type == "class_":
                WebDriverWait(cls.driver, timeout).until(
                    lambda driver: driver.find_elements_by_class_name(value))
                ele = cls.driver.find_elements_by_class_name(value)
            else:
                print("No such locate element way {}".format(ele_type))
        except NotImplementedError as e:
            log.debug(e)
        except TimeoutError as e:
            log.debug(e)
            # else:
            # return ele
        finally:
            return ele

    @classmethod
    def swipe(cls, direction, during):
        element = cls.driver.find_element_by_class_name(
            "android.widget.LinearLayout")
        if direction == 'up':
            size = element.size
            width = size["width"]
            height = size["height"]
            log.info(width+height)
            cls.driver.swipe(width / 2, height * 3 / 4,
                             width / 2, height / 4, during)

        elif direction == 'down':
            size = element.size
            width = size["width"]
            height = size["height"]
            log.info(width+height)
            cls.driver.swipe(width / 2, height / 4, width /
                             2, height * 3 / 4, during)

        elif direction == 'left':
            size = element.size
            width = size["width"]
            height = size["height"]
            log.info(width+height)
            cls.driver.swipe(width * 3 / 4, height / 2,
                             width / 4, height / 2, during)

        elif direction == 'right':
            size = element.size
            width = size["width"]
            height = size["height"]
            log.info(width+height)
            cls.driver.swipe(width / 4, height / 2, width *
                             3 / 4, height / 2, during)

        else:
            log.info('Argument is Error')

    @classmethod
    def click(cls, ele_type, value, name, timeout=15):
        try:
            if ele_type == 'ui':
                value = ('new UiSelector().className("android.widget.TextView")'
                         '.text("{}")').format(value)
            log.debug('     ---> {}'.format(value))
            cls.find_ele(ele_type, timeout, value).click()
            log.info('Tab {}'.format(name))
            return True
        except Exception as e:
            log.debug(e)
            return False

    @classmethod
    def find_text(cls, text):  # to find Get start
        log.info('Finding {}'.format(text))
        for i in range(1, 5):
            try:
                els = cls.find_ele('class_', 15, 'android.widget.TextView')
                for n in range(len(els)):
                    el = els[n].get_attribute("text")
                    if el == text:
                        return True
                sleep(5)
            except Exception as e:
                log.info(e)
                sleep(3)
        return False

    @classmethod
    def input(cls, ele, text):
        try:
            input_field = cls.find_ele('id', 15, ele)
            input_field.clear()
            '''
            cls.driver.keyevent(123)    #delete key  
            for i in range(0,len(dutName)):
                cls.driver.keyevent(67)       
            sleep(1)
            '''
            log.info('Input password {}'.format(text))
            input_field.send_keys(text)
            sleep(0.5)
            cls.send_key(4)  # back button
            return True
        except Exception as e:
            log.error('Cannot find input field: {}'.format(e))
            return False

    @classmethod
    def tap_pic(cls, src_pic, obj_pic):
        for i in range(4):
            try:
                cls.driver.get_screenshot_as_file(src_pic)
                pos = coordinate(src_pic, obj_pic)
                log.info('Click position ({},{})'.format(pos[0], pos[1]))
                cls.driver.tap([(pos[0], pos[1]), (pos[0], pos[1])], 500)
                return True
            except Exception as e:
                log.info('Cannot find match: {}'.format(e))
                sleep(4)
