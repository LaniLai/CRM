# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

# 重构Django的Admin
from BossAdmin.service.admin_base import ModelAdmin
from BossAdmin.service import sites
from repository import models


class CustomerInfoAdmin(ModelAdmin):
    list_display = ['id', 'name', 'source', 'contact_type', 'contact', 'consultant', 'status', 'date']
    list_filter = ['source', 'consultant', 'status', 'date']
    search_fields = ['contact', 'consultant__name']
    readonly_fields = ['status', 'contact']
    filter_horizontal = ['consult_courses']

    actions = ['change_status', ]

    def change_status(self, request, query_sets):
        query_sets.update(status=0)


class CourseRecordAdmin(ModelAdmin):
    actions = ['initialization_studyRecord']


sites.site.register(models.CustomerInfo, CustomerInfoAdmin)
sites.site.register(models.UserProfile)
sites.site.register(models.CourseRecord)
