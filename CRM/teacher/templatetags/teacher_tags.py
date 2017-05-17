# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from django import template
from django.utils.safestring import mark_safe
from django.db.models import Q, Avg
from repository import models
from functools import reduce

register = template.Library()


@register.filter
def get_attendance_count(stu_obj, cls_obj):
    """
    获取出勤次数
    根据班级获取所有的上课记录
    :param stu_obj:
    :return:
    """
    # 获取该班级的所有上课记录
    course_record_list = models.CourseRecord.objects.filter(class_grade=cls_obj)
    # 查询学员的所有上课记录状态为已签到的次数
    stu_attendance_count = models.StudyRecord.objects.filter\
        (student=stu_obj, course_record__in=course_record_list, show_status=1).count()
    return stu_attendance_count


@register.filter
def get_late_count(stu_obj, cls_obj):
    """
    获取迟到, 早退, 缺勤次数
    :param stu_obj:
    :param cls_obj:
    :return:
    """
    # 获取该班级的所有上课记录
    course_record_list = models.CourseRecord.objects.filter(class_grade=cls_obj)
    stu_late_count = models.StudyRecord.objects.filter\
        (Q(student=stu_obj), Q(course_record__in=course_record_list), ~Q(show_status=1)).count()
    return stu_late_count


@register.filter
def get_avg_score(stu_obj, cls_obj):
    """
    获取该学员的平均成绩
    获取该学生的所有学习记录的成绩, 进行统计平均值
    分母不可为0
    :param stu_obj:
    :return:
    """
    # 获取该班级的所有上课记录
    course_record_list = models.CourseRecord.objects.filter(class_grade=cls_obj)
    stu_study_score_list = models.StudyRecord.objects.filter(
        student=stu_obj, course_record__in=course_record_list
    ).values('score')

    score_sum = sum(map(lambda x: x['score'], stu_study_score_list))
    return '%.2f' %(score_sum/len(course_record_list), )
