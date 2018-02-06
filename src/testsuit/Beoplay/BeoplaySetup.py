"""
Bruce zhu 2018/01/09
"""
import json
import re
import sys
import os
from time import sleep
from src.beoplay import Beoplay
from src.common.AppiumScreenshot import ScreenShot
from src.common.cfg import Config
from src.common.Logger import Logger
from src.ase.AseInfo import AseInfo
from src.common.adb import adb

log = Logger("main").logger()


class BeoplaySetup(object):
    def __init__(self):
        if not adb.check_device_status():
            sys.exit()
        with open('./config/beoplayEle.json') as json_file:
            self.beo = json.load(json_file)
        testconfig = Config('./config/testconfig.ini')
        testconfig.cfg_load()
        self.tcfg = testconfig.cfg

    def connect_phone(self):
        log.info('Connecting with your phone ...')
        try:
            Beoplay.connect(platformName=self.tcfg.get('App', 'platformName'),
                            deviceName=self.tcfg.get('App', 'deviceName'),
                            timeout=self.tcfg.get('App', 'timeout'),
                            appPackage=self.tcfg.get('Beoplay', 'appPackage'),
                            appActivity=self.tcfg.get('Beoplay', 'appActivity'),
                            remote_server=self.tcfg.get('Appium', 'remote_server'),
                            )
            return True
        except Exception as e:
            log.error('Cannot connect to your phone: {}'.format(e))
            return False

    def shot(self, name):
        ScreenShot(Beoplay.driver).get_screenshot(self.tcfg.get('Log', 'screen_shot_path'), name)

    def verify(self, action, name):
        if not action:
            log.info(name)
            self.shot(name)
            sys.exit()

    def click(self, type_name, name, timeout=15):
        value = self.beo.get(name)
        if value is None:
            value = name
        if not Beoplay.click(type_name, value, name, timeout=timeout):
            name = 'cannot_find_' + name
            log.info(name)
            self.shot(name)
            sys.exit()

    def run(self):
        ase_info = AseInfo()
        if not self.connect_phone():
            sys.exit()
        for i in range(1, 10):

            log.info('--------------------------------This is the {} times'.format(i))
            version_path = self.tcfg.get('OTA', 'version_path')
            test_version = self.tcfg.get('OTA', 'test_version')
            latest_version = self.tcfg.get('DUT', 'latest_version')
            ip = self.tcfg.get('DUT', 'ip')
            bt_name = self.tcfg.get('DUT', 'bt_name')
            if 'true' in self.tcfg.get('OTA', 'ota_test').lower():
                if not ase_info.update_version(version_path, test_version, ip):
                    sys.exit()
            log.info('Factory reset for {}'.format(bt_name))
            ase_info.reset(ip)
            sleep(self.tcfg.getint('DUT', 'reset_time'))
            log.info('Starting App...')
            Beoplay.close_and_launch_app()
            self.click('ui', 'add_device')
            self.click('id', 'continue')
            sleep(1)
            # loc = re.findall('(\d+)', self.tcfg.get(self.tcfg.get('App', 'deviceName'), 'permission_allow'))
            # Beoplay.driver.tap([(loc[0], loc[1]), (loc[2], loc[3])], 500)
            src_pic = self.tcfg.get('Log', 'screen_shot_path') + 'page.png'
            obj_pic = self.tcfg.get('data', 'pic_allow')
            Beoplay.tap_pic(src_pic, obj_pic)

            # Beoplay.start_activity('com.android.packageinstaller', '.permission.ui.GrantPermissionsActivity')
            # Beoplay.click_allow()
            sleep(2)
            self.verify(Beoplay.search_sample(bt_name), 'cannot_find_sample')
            sleep(10)
            self.verify(Beoplay.input(self.beo.get('password'), self.tcfg.get('Wifi', 'password')),
                        'cannot_find_input')
            self.click('id', 'connect')
            log.info('Try to find connect button')
            sleep(10)
            for j in range(100):
                if Beoplay.find_text(self.beo.get('next')):
                    break
                if Beoplay.find_text('Failed'):
                    self.click('ui', self.beo.get('retry'))
                sleep(5)
            self.click('ui', 'next', timeout=self.tcfg.getint('OTA', 'update_time'))
            self.click('ui', 'next')
            self.click('ui', 'finish_setup')
            sleep(3)
            if Beoplay.find_text(self.beo.get('beomusic')) or Beoplay.find_text(self.beo.get('google_cast')):
                self.click('id', 'back')
                self.click('class', 'setting')  # click('ui', 'no_thanks')
                self.click('ui', 'product_info')
            sn = self.tcfg.get('DUT', 'sn')

            self.verify(Beoplay.find_text(sn), 'cannot_find_sn_{}'.format(sn))
            self.verify(Beoplay.find_text(latest_version), 'cannot_find_version_{}'.format(latest_version))
            ip = Beoplay.find_ele('class_', 15, 'android.widget.TextView')[2].get_attribute("text")
            self.click('id', 'back')
            self.click('ui', bt_name[:18])
            self.click('ui', 'remove_device')
            # verify(Beoplay.click('id', beo.get('plus')), 'cannot_find_plus_icon')


