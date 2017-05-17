# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from django.forms import ModelForm
from repository import models


class AddClsRecordForm(ModelForm):
    class Meta:
        model = models.CourseRecord
        fields = "__all__"

    def __new__(cls, *args, **kwargs):
        # cls.base_fields 即所显示Model_Form的所有字段
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class': 'form-control'})
        return ModelForm.__new__(cls)