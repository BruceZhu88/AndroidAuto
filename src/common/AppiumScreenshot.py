#!/usr/bin/env python
# coding=utf-8

import os
import shutil
# import platform
import tempfile
import time
from PIL import Image
from src.common.Logger import Logger

log = Logger("main").logger()
PATH = lambda p: os.path.abspath(p)
TEMP_FILE = PATH(tempfile.gettempdir() + "/temp_screen.png")


class ScreenShot(object):
    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def get_time():
        return time.strftime('%Y%m%d_%H-%M-%S', time.localtime())

    def get_screenshot(self, path, name, form='png'):
        if not os.path.isdir(path):
            os.makedirs(path)
        file_path = path + name + '_' + self.get_time() + "." + form
        self.driver.get_screenshot_as_file(file_path)
        log.info(file_path)

    def get_screenshot_by_element(self, element):
        self.driver.get_screenshot_as_file(TEMP_FILE)

        location = element.location
        size = element.size
        box = (location["x"], location["y"], location["x"] +
               size["width"], location["y"] + size["height"])

        image = Image.open(TEMP_FILE)
        newImage = image.crop(box)
        newImage.save(TEMP_FILE)

        return self

    def get_screenshot_by_custom_size(self, start_x, start_y, end_x, end_y):
        self.driver.get_screenshot_as_file(TEMP_FILE)
        box = (start_x, start_y, end_x, end_y)

        image = Image.open(TEMP_FILE)
        newImage = image.crop(box)
        newImage.save(TEMP_FILE)

        return self

    @staticmethod
    def write_to_file(dirPath, imageName, form="png"):
        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)
        shutil.copyfile(TEMP_FILE, PATH(
            dirPath + "/" + imageName + "." + form))

    @staticmethod
    def load_image(image_path):
        if os.path.isfile(image_path):
            load = Image.open(image_path)
            return load
        else:
            raise Exception("%s is not exist" % image_path)

    # http://testerhome.com/topics/202
    def same_as(self, load_image, percent):
        import math
        import operator

        # image1 = Image.open('D:\workspace\APP_TEST\screen\Sony_Xperia_Z\Bluetooth.png')
        # image2 =
        # Image.open('D:\workspace\APP_TEST\screen\Sony_Xperia_Z\USB.png')

        image1 = Image.open(TEMP_FILE)
        image2 = load_image

        histogram1 = image1.histogram()
        histogram2 = image2.histogram()

        differ = math.sqrt(reduce(operator.add,
                                  list(map(lambda a, b: (a - b) ** 2, histogram1, histogram2))) / len(histogram1))

        print(differ)
        if differ <= percent:
            return True
        else:
            return False


if __name__ == "__main__":
    extend = ScreenShot('driver')
    extend.same_as('load_image', 0)
