
from time import sleep
from src.common.Logger import Logger
from src.common.app import App

log = Logger("main").logger()


class OneApp(App):

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
