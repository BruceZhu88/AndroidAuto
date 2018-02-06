
import subprocess
from src.common.Logger import Logger
log = Logger("main").logger()


class adb(object):

    @staticmethod
    def check_device_status():
        try:
            s = subprocess.Popen('adb devices', shell=True, stdout=subprocess.PIPE)
            pipe = s.stdout.readlines()
            if len(pipe) < 2:
                log.error('Cannot find adb device!')
                return False
            if 'device' in pipe[1].decode('utf-8'):
                return True
        except Exception as e:
            log.error('Some thing wrong with your adb: {}'.format(e))
            return False
