"""
Created on Jan 3, 2017
@author: Bruce zhu
"""
import urllib.request
import requests
import re
import json
import os
import logging
from threading import Thread, Lock
from time import sleep
from urllib import request
# from urllib.error import URLError
from src.ase.AseWebData import *
from src.common.Logger import Logger
log = Logger("main").logger()
lock = Lock()


class AseInfo(object):
    def __init__(self):
        self.ip = 'NA'
        self.device = 'NA'
        self.urlSetData = "http://{}/api/setData?{}"
        self.urlGetData = "http://{}/api/getData?{}"
        self.urlGetRows = "http://{}/api/getRows?{}"
        self.devices_list = []
        self.threads = []
        self.status = 0

    def request_url(self, url, data=None, timeout=None):
        status = ""
        try:
            req = request.Request(url, data)
            if timeout is not None:
                res = request.urlopen(req, timeout=timeout)
            else:
                res = request.urlopen(req)
            status = res.status
            # data = urllib.request.urlopen(url, timeout=8)
            text = res.read().decode('utf8')
        except Exception as e:
            logging.debug(e)
            text = "error"
        return {"text": text, "status": status}

    @staticmethod
    def check_url_status(url, timeout=20.0):
        try:
            req = request.Request(url)
            response = urllib.request.urlopen(req, timeout=timeout)
            # status = response.status
            return True
            # except URLError as e:
        except Exception as e:
            # logging.debug("Cannot connect {}: {}".format(url, e))
            return False
            """
            if hasattr(e, 'reason'):    # urlError
                print('We failed to reach a server')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):    # httpError
                print('The server could not fulfill the request.')
                print('Error code: ', e.code)
            """

    def transfer_data(self, request_way, ip, value, timeout=None):
        value_str = urllib.parse.urlencode(value, encoding="utf-8")
        if "+" in value_str:
            value_str = value_str.replace('+', '')
        if "True" in value_str:
            value_str = value_str.replace('True', 'true')
        if "False" in value_str:
            value_str = value_str.replace('False', 'false')
        if "%27" in value_str:
            value_str = value_str.replace('%27', '%22')
        if request_way == "get":
            url = self.urlGetData.format(ip, value_str, timeout=timeout)
            return self.request_url(url)
        elif request_way == "getRows":
            url = self.urlGetRows.format(ip, value_str, timeout=timeout)
            return self.request_url(url)
        elif request_way == "set":
            url = self.urlSetData.format(ip, value_str, timeout=timeout)
            return self.request_url(url)
        else:
            logging.info("No such request way: {}".format(request_way))

    @staticmethod
    def ota_update(ip, files):
        """
        ASE OTA Update
        :param ip: Device ip
        :param files: Must be dict
        :return: Number type(post status)
        """
        url = "http://{}/page_setup_swupdate.fcgi?firmwareupdate=1".format(ip)
        req = requests.post(url=url, files=files)
        return req.status_code

    def trigger_update(self, ip):
        return self.transfer_data("set", ip, update_para)["status"]

    def get_info(self, x, ip, timeout=None):
        try:
            if x == 'basicInfo':
                resp_value = self.request_url('http://{0}/index.fcgi'.format(ip))['text']
                data = re.findall('dataJSON = \'(.*)\';', resp_value)[0]
                resp_value = self.request_url('http://{0}/page_status.fcgi'.format(ip))['text']
                product_id = re.findall('var productId = \'(.*)\';', resp_value)[0]
                jd = json.loads(product_id, encoding='utf-8')
                sn = ''
                for i in jd["beoGphProductIdData"]["serialNumber"]:
                    sn = sn + str(i)
                data = json.loads(data, encoding='utf-8')
                info = {'modelName': data['beoMachine']['modelName'],
                        'model': data['beoMachine']['model'],
                        'productName': data['beoMachine']['setup']['productName'],
                        'bootloaderVersion': data['beoMachine']['fepVersions']['bootloaderVersion'],
                        'appVersion': data['beoMachine']['fepVersions']['appVersion'],
                        'sn': sn}
                return info
            elif x == 'device_name':
                data = self.transfer_data("get", ip, deviceName_para, timeout=timeout)['text']
                device_name = json.loads(data, encoding='utf-8')[0]['string_']
                return device_name
            elif x == 'device_version':
                data = self.transfer_data("get", ip, displayVersion_para)['text']
                data = json.loads(data, encoding='utf-8')
                return data[0]["string_"]
            elif x == 'wifi_device':
                data = self.transfer_data("get", ip, WirelessSSID_para)['text']
                data = json.loads(data, encoding='utf-8')
                return data[0]["string_"]
            # elif x == 'wifi_level':
            #    data = self.transfer_data("get", ip, wifiSignalLevel_para)
            #    return re.findall(':\\[(.+)\\]}', data)[0]
            elif x == 'volume_default':
                data = self.transfer_data("get", ip, volumeDefault_para)['text']
                data = json.loads(data, encoding='utf-8')
                return data[0]["i32_"]
            elif x == 'volume_max':
                data = self.transfer_data("get", ip, volumeMax_para)['text']
                data = json.loads(data, encoding='utf-8')
                return data[0]["i32_"]
            elif x == 'bt_open':
                data = self.transfer_data("get", ip, pairingAlwaysEnabled_para)['text']
                data = json.loads(data, encoding='utf-8')
                return data[0]["bool_"]
            elif x == 'bt_reconnect':
                data = self.transfer_data("get", ip, autoConnect_para)['text']
                data = json.loads(data, encoding='utf-8')
                connect_mode = data[0]["bluetoothAutoConnectMode"]
                if connect_mode == 'manual':
                    return 'Manual'
                elif connect_mode == 'automatic':
                    return 'Automatic'
                else:
                    return 'Disable'
            elif x == 'bt':
                data = self.transfer_data("getRows", ip, pairedPlayers_para)['text']
                value = json.loads(data, encoding='GBK')  # Avoid chinese strings
                return value
            else:
                return 'NA'
        except Exception as e:
            logging.debug('cmd = {0}, error: {1}'.format(x, e))
            return 'NA'

    def scan_wifi(self, ip):
        data = self.transfer_data("getRows", ip, network_scan_results_para)
        return data

    def pair_bt(self, pair, ip):
        if pair == 'pair':
            para = pairBT_para
        elif pair == 'cancel':
            para = pairCancelBT_para
        self.transfer_data("set", ip, para)

    def reset(self, ip):
        self.transfer_data("set", ip, factoryResetRequest_para)

    def change_product_name(self, name, ip):
        self.transfer_data("set", ip, set_deviceName_para(name))

    def log_submit(self, ip):
        values = self.transfer_data("set", ip, logReport_para)
        return values["status"]

    def bt_open_set(self, open_enable, ip):
        self.transfer_data("set", ip, set_pairingAlwaysEnabled(open_enable))

    def bt_remove(self, bt_mac, ip):
        bt_mac = bt_mac.replace(":", "_")
        self.transfer_data("set", ip, bt_remove_para(bt_mac))

    def bt_reconnect_set(self, status, ip):
        if status == 'Manual':
            mode = 'manual'
        elif status == 'Automatic':
            mode = 'automatic'
        elif status == 'Disable':
            mode = 'none'
        else:
            return
        self.transfer_data("set", ip, set_autoConnect(mode))

    def update_version(self, file_path, version, ip_addr):
        url = "http://{}/index.fcgi".format(ip_addr)
        log.info('Checking version')
        if not self.check_url_status(url, timeout=6):
            log.error('Cannot find your device in network!')
            return False
        if self.get_info('device_version', ip_addr) == version:
            log.info('Current version is test version {}'.format(version))
            return True
        if not os.path.exists(file_path):
            log.error('{} is not exists!'.format(file_path))
            return False
        files = {
            'file': open(file_path, 'rb')
        }
        log.info('Uploading file ...')
        if self.ota_update(ip_addr, files=files) != 200:
            log.error("Upload file failed!")
            return False
        self.trigger_update(ip_addr)
        sleep(80)
        log.info('Checking update status...')
        n = 0
        while not self.check_url_status(url, timeout=6):
            n += 1
            if n >= 50:
                log.error('Cannot find [{}] in network'.format(ip_addr))
                return False
        log.info('Checked sample in network [{}]'.format(ip_addr))
        if self.get_info('device_version', ip_addr) == version:
            log.info('Update successfully to [{}]'.format(version))
            return True
        else:
            log.error("Upload ASE OTA file failed!")
            return False


if __name__ == "__main__":
    ase_info = AseInfo()
    files = {
        'file': open(r'‪D:\bruce\Tymphany\Test_case\CA17\version\ase2ca17s810-release-1-0-15059-28653020', 'rb')
    }
    ase_info.ota_update("192.168.1.160", files=files)