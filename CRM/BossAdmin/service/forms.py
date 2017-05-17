# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from django.forms import ModelForm


def create_dynamic_form(boss_admin_class, status=False):
    """
    动态生成ModelForm组件
    :param boss_admin_class:
    :param status: 是否为添加状态 True表示添加
    :return:
    """
    class Meta:
        model = boss_admin_class.model
        fields = '__all__'
        if not status:
            exclude = boss_admin_class.readonly_fields
            boss_admin_class.status = False
        else:
            boss_admin_class.status = True

    def __new__(cls, *args, **kwargs):
        for field_name in cls.base_fields:
            field_obj = cls.base_fields[field_name]
            field_obj.widget.attrs.update({'class': 'form-control'})
        return ModelForm.__new__(cls)

    dynamic_form = type('DynamicModelForm', (ModelForm, ), {'Meta': Meta, '__new__': __new__})
    return dynamic_form
