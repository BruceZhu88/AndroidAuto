
import logging
from src.common.app import App


class Android(App):


    @classmethod
    def click_allow(cls):
        allow = cls.find_ele('id', 15, 'com.android.packageinstaller:id/permission_allow_button')
        if allow is not None:
            allow.click()
