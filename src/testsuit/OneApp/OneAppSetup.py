"""
Bruce zhu 2018/01/18
"""
import json
import re
import sys
from time import sleep
from src.OneApp import OneApp
from src.common.AppiumScreenshot import ScreenShot
from src.common.cfg import Config
from src.common.Logger import Logger
from src.ase.AseInfo import AseInfo
from src.common.adb import adb

log = Logger("main").logger()


class OneAppSetup(object):
    def __init__(self):
        if not adb.check_device_status():
            sys.exit()
        with open('./config/OneAppEle.json') as json_file:
            self.one = json.load(json_file)
        testconfig = Config('./config/testconfig.ini')
        testconfig.cfg_load()
        self.cfg = testconfig.cfg

    def connect_phone(self):
        log.info('Connecting with your phone ...')
        try:
            OneApp.connect(platformName=self.cfg.get('App', 'platformName'),
                            deviceName=self.cfg.get('App', 'deviceName'),
                            timeout=self.cfg.get('App', 'timeout'),
                            appPackage=self.cfg.get('OneApp', 'appPackage'),
                            appActivity=self.cfg.get('OneApp', 'appActivity'),
                            remote_server=self.cfg.get('Appium', 'remote_server'),
                            )
            return True
        except Exception as e:
            log.error('Cannot connect to your phone: {}'.format(e))
            return False

    def shot(self, name):
        ScreenShot(OneApp.driver).get_screenshot(self.cfg.get('Log', 'screen_shot_path'), name)

    def verify(self, action, name):
        if not action:
            log.info(name)
            self.shot(name)
            sys.exit()

    def click(self, type_name, name, timeout=15, var=True):
        value = self.one.get(name) if var else name
        if value is None:
            value = name
        if not OneApp.click(type_name, value, name, timeout=timeout):
            name = 'cannot_find_' + name
            log.info(name)
            self.shot(name)
            sys.exit()

    def run(self):
        ase_info = AseInfo()
        if not self.connect_phone():
            sys.exit()
        log.info('Starting App...')
        # self.click('id', 'ignore')
        self.click('ui', 'sign_email')
        OneApp.input(self.one.get('sign_user'), 'jialin.zhu88@gmail.com')
        OneApp.input(self.one.get('sign_pwd'), '459643556')
        self.click('id', 'sign_in')
        self.click('id', 'add_product', timeout=80)
        sleep(5)
        # Tap Allow button
        src_pic = self.cfg.get('Log', 'screen_shot_path') + 'page.png'
        obj_pic = self.cfg.get('data', 'pic_allow')
        OneApp.tap_pic(src_pic, obj_pic)

        sleep(1)
        OneApp.send_key(4)
        sleep(2)
        for i in range(1, 2):

            log.info('--------------------------------This is the {} times'.format(i))
            version_path = self.cfg.get('OTA', 'version_path')
            test_version = self.cfg.get('OTA', 'test_version')
            latest_version = self.cfg.get('DUT', 'latest_version')
            ip = self.cfg.get('DUT', 'ip')
            bt_name = self.cfg.get('DUT', 'bt_name')
            sn = self.cfg.get('DUT', 'sn')
            '''''
            if 'true' in self.cfg.get('OTA', 'ota_test').lower():
                if not ase_info.update_version(version_path, test_version, ip):
                    sys.exit()
            log.info('Factory reset for {}'.format(bt_name))
            '''
            # ase_info.reset(ip)
            # sleep(self.cfg.getint('DUT', 'reset_time'))
            self.click('id', 'add_product')
            sleep(5)
            # test = OneApp.find_ele('a_id', 15, self.one.get('product_name'))
            # print(len(test))
            src_pic = self.cfg.get('Log', 'screen_shot_path') + 'page.png'
            obj_pic = self.cfg.get('data', 'sample_name').format(bt_name)
            OneApp.tap_pic(src_pic, obj_pic)
            '''
            OneApp.driver.find_element_by_xpath("//android.widget.TextView[contains(@text,'Beoplay M3_28889998')]").click()
            OneApp.search_sample(self.cfg.get('DUT', 'bt_name'))
            if OneApp.find_text(self.cfg.get('DUT', 'bt_name')):
                print('find it')
                self.click('ui', self.cfg.get('DUT', 'bt_name'), timeout=60, var=False)
            '''
            self.click('id', 'next_add', timeout=60)
            if not OneApp.find_text('Wifi network'):
                log.error('Cannot find password field!')
                sys.exit()
            OneApp.input(self.one.get('input_pwd'), self.cfg.get('Wifi', 'password'))
            self.click('id', 'next_wifi', timeout=60)
            self.click('id', 'ok_button', timeout=60)

            for i in range(50):
                if OneApp.find_text('GET STARTED'):
                    self.click('ui', 'GET STARTED', var=False)
                    self.click('ui', 'AGREE', var=False)
                    self.click('ui', 'NOT RIGHT NOW', var=False)
                    self.click('ui', 'DONE', var=False)
                    break
                if OneApp.find_text('DONE'):
                    self.click('ui', 'DONE', var=False)
                    break
                sleep(10)
            self.click('ui', bt_name.upper(), timeout=60)
            OneApp.swipe('up', 200)
            OneApp.swipe('up', 200)
            OneApp.swipe('up', 200)
            OneApp.swipe('up', 200)
            self.click('ui', 'About product', var=False)
            sleep(8)
            self.verify(OneApp.find_text(sn), 'cannot_find_sn_{}'.format(sn))
            self.verify(OneApp.find_text(latest_version), 'cannot_find_version_{}'.format(latest_version))
            OneApp.send_key(4)
            self.click('ui', 'remove_product')
            self.click('ui', 'another_reason')


