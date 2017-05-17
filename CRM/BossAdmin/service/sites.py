# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from BossAdmin.service import admin_base


class BossAdminSite(object):
    def __init__(self):
        self.registry = {}

    def register(self, model, bossadmin_class=None):
        """注册boss_admin表"""
        # 获取对应表的名称和表对应APP名称
        app_name = model._meta.app_label
        model_name = model._meta.model_name
        if not bossadmin_class:
            bossadmin_class = admin_base.ModelAdmin()
        else:
            bossadmin_class = bossadmin_class()
        bossadmin_class.model = model
        if app_name not in self.registry:
            self.registry[app_name] = {}
        self.registry[app_name][model_name] = bossadmin_class


site = BossAdminSite()