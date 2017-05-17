# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer
from django import template
from django.utils.safestring import mark_safe
import datetime
register = template.Library()


@register.simple_tag
def html_row(obj, boss_admin_class):
    html = '<td class="action-checkbox"><input row-select="true" value="%s" type="checkbox"></td>' %obj.id
    if boss_admin_class.list_display:
        for num, column_name in enumerate(boss_admin_class.list_display):
            column_obj = boss_admin_class.model._meta.get_field(column_name)
            if column_obj.choices:
                column_data = getattr(obj, 'get_%s_display' % column_name)()
            else:
                column_data = getattr(obj, column_name)
            if num == 0:
                html += '<td><a href="%s/%s/">%s</a></td>' %(obj.id, 'change',column_data)
            else:
                html += '<td>%s</td>' % column_data
    else:
        html += '<td><a href="%s/change/">%s</a><td>' %(obj.id, obj)
    return mark_safe(html)


@register.simple_tag
def html_filter(filter, boss_admin_class):
    """
    构建查询条件下拉框
    :param filter: 循环的查询条件
    :param boss_admin_class: 被选中的表
    :return:
    """
    filter_obj = boss_admin_class.model._meta.get_field(filter)
    try:
        filter_html = '<select name="%s">' %filter
        for choice in filter_obj.get_choices():
            selected = ''
            if filter in boss_admin_class.search_dict:
                if str(choice[0]) == boss_admin_class.search_dict.get(filter):
                    selected = 'selected'
            option = '<option value="{0}" {1}>{2}</option>'.format(choice[0], selected, choice[1])
            filter_html += option

    except AttributeError:
        filter_html = '<select name="{0}__gte">' .format(filter)
        if filter_obj.get_internal_type() in ('DateField', 'DateTimeField'):
            current_time = datetime.datetime.now()
            time_list = [
                ['', '--------'],
                [current_time, '今天'],
                [current_time - datetime.timedelta(7), '七天内'],
                [current_time.replace(day=1), '本月内'],
                [current_time - datetime.timedelta(90), '三个月内'],
                [current_time.replace(month=1, day=1), '本年内']
            ]
            for item in time_list:
                selected = ''
                timeTostr = '' if not item[0] else '{year}-{month}-{day}'\
                    .format(year=item[0].year, month=item[0].month, day=item[0].day)
                if '%s__gte' %filter in boss_admin_class.search_dict:
                    if timeTostr == boss_admin_class.search_dict.get('%s__gte' %filter):
                        selected = 'selected'
                option = '<option value="{0}" {1}>{2}</option>'.format(timeTostr, selected, item[1])
                filter_html += option
    filter_html += '</select> '

    return mark_safe(filter_html)


@register.filter
def get_order_by_index(ordered_dict):
    """
    判断在搜索时是否有某字段的排序
    :param ordered_dict:
    :return:
    """
    return list(ordered_dict.values())[0] if ordered_dict else ''


@register.filter
def get_search_dict(boss_admin_class):
    """
    排序是否有搜索条件
    :param boss_admin_class:
    :return:
    """
    search_html = ''
    if boss_admin_class.search_dict:
        for k, v in boss_admin_class.search_dict.items():
            search_html += '&{0}={1}'.format(k,v)
    return mark_safe(search_html)


@register.filter
def get_verbose_name(column, boss_admin_class):
    column_obj = boss_admin_class.model._meta.get_field(column)
    if not column_obj.verbose_name:
        verbose_name = column
    else:
        verbose_name = column_obj.verbose_name
    return mark_safe(verbose_name)


@register.filter
def get_icons(column, ordered_dict):
    """
    根据排序字段获取相应图标
    :param column:
    :param ordered_dict:
    :return:
    """
    if column not in ordered_dict:
        return ''
    order_by_index = ordered_dict[column]
    if order_by_index.startswith('-'):
        status = 'down'
    else:
        status = 'up'
    icon = '<i class="fa fa-arrow-%s" aria-hidden="true"></i>' %status
    return mark_safe(icon)


@register.filter
def get_placeholder(boss_admin_class):
    placeholder_text = ''
    for search_field in boss_admin_class.search_fields:
        if '__' in search_field:
            search_field, v = search_field.rsplit('__')
        column_obj = boss_admin_class.model._meta.get_field(search_field)
        if not column_obj.verbose_name:
            placeholder_text += '%s/' %search_field
        else:
            placeholder_text += '%s/' %column_obj.verbose_name
    return mark_safe(placeholder_text)


@register.simple_tag
def get_sorted_column(column, column_index, ordered_dict):
    """
    生成过滤条件
    :param column: 当前循环字段
    :param column_index: 字段索引
    :param ordered_dict: 排列过的字段
    :return:
    """
    if column in ordered_dict:
        order_by_index = ordered_dict[column]
        if not order_by_index.startswith('-'):
            order_by_index = '-{}'.format(order_by_index)
        else:
            order_by_index = order_by_index.strip('-')
        return order_by_index
    return column_index


@register.filter
def get_path(path):
    """
    当前路径位置渲染
    :param path:
    :return:
    """
    html = '<a href="/bossadmin/">Home</a> '
    for item in path.split('/'):
        if not item or item == 'bossadmin':
            continue
        html += ' > %s' %item.title()
    return mark_safe(html)


@register.filter
def get_field_text(field, form_obj):
    # choices选项  bug
    return getattr(form_obj.instance, field)


@register.simple_tag
def get_available_m2m_data(field_name, form_obj, boss_admin_class):
    """
    获取可用的M2M
    :param field_name:
    :param form_obj:
    :param boss_admin_class:
    :return:
    """
    field_obj = boss_admin_class.model._meta.get_field(field_name)
    m2m_set = set(field_obj.related_model.objects.all())
    if not boss_admin_class.status:
        chosen_set = set(getattr(form_obj.instance, field_name).all())
        return m2m_set - chosen_set
    return m2m_set


@register.simple_tag
def get_chosen_m2m_data(field_name, form_obj, boss_admin_class):
    if not boss_admin_class.status:
        return getattr(form_obj.instance, field_name).all()


@register.filter
def get_relevant_data(delete_obj):
    """
    显示删除对象先关联的数据
    :param delete_obj: 删除的对象
    :return:
    """
    html = '<ul>'
    # print(delete_obj._meta.many_to_many)
    for reversed_fk_obj in delete_obj._meta.related_objects:
        related_table_name = reversed_fk_obj.name
        related_lookup_key = '%s_set' %related_table_name
        related_objs = getattr(delete_obj, related_lookup_key).all()
        html += '<li>%s<ul>' %related_table_name
        if reversed_fk_obj.get_internal_type() == 'ManyToManyField':
            # 多对多字段无需深入查找
            for item in related_objs:
                html += '<li>%s</li>' %item
        else:
            for item in related_objs:
                html += '<li><a href="/bossadmin/%s/%s/%s/change/">%s</a></li>' \
                        %(item._meta.app_label,item._meta.model_name,item.id,item)
                html += get_relevant_data(item)
        html += '</ul></li>'
    html += '</ul>'
    return html

