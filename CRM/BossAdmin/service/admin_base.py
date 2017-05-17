# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer
from django.shortcuts import render


class ModelAdmin(object):
    def __init__(self):
        self.actions.extend(self.default_actions)
    list_display = []
    list_filter = []
    search_fields = []
    readonly_fields = []
    filter_horizontal = []
    list_per_page = 20
    default_actions = ['delete_selected_objs']
    actions = []

    def delete_selected_objs(self, request, query_sets):
        return render(request, 'modelrowdelete.html', {'query_sets': query_sets})