# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer


class BaseResponse(object):
    def __init__(self):
        self.status = True
        self.message = None
        self.data = None
        self.error = None
