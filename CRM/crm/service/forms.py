# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from django import forms
from django.forms import ModelForm
from repository import models


class CustomerForm(ModelForm):
    class Meta:
        model = models.CustomerInfo
        fields = "__all__"
        exclude = ['consult_content', 'status', 'consult_courses', 'source', 'id_num']
        readonly_fields = ['contact_type', 'contact', 'consultant', 'referral_from']

    def __new__(cls, *args, **kwargs):
        # cls.base_fields 即所显示Model_Form的所有字段
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class':'form-control'})

            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
        return ModelForm.__new__(cls)

    def clean(self):
        if self.errors:
            raise forms.ValidationError(("Please fix errors before re-submit."))
        if self.instance.id is not None:
            for field in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance, field)
                form_val = self.cleaned_data.get(field)
                print("filed differ compare:",old_field_val,form_val)
                if old_field_val != form_val:
                    self.add_error(field, "字段内容不能随意变更。")


class EnrollmentForm(ModelForm):
    class Meta:
        model = models.StudentEnrollment
        fields = "__all__"
        exclude = ['contract_approved_date', 'customer', 'consultant']
        readonly_fields = ['contract_agreed', 'contract_signed_date']

    def __new__(cls, *args, **kwargs):
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class': 'form-control'})
            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
        return ModelForm.__new__(cls)




