# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from django import conf
import importlib


def bossadmin_auto_discover():
    """
    动态导入模块
    :return:
    """
    for app_name in conf.settings.INSTALLED_APPS:
        try:
            importlib.import_module('%s.bossadmin' %app_name)
            # moudel = __import__('%s.bossadmin' %app_name)
        except ImportError:
            pass







