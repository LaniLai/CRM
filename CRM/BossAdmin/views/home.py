# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from BossAdmin.service.sites import site
from BossAdmin.service import app_setup
from BossAdmin.service import forms
from BossAdmin.utlis import MyPager
import json

app_setup.bossadmin_auto_discover()


class IndexView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(IndexView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html', {'registry': site.registry})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        pass


class ModelDetailView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ModelDetailView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, app_name, model_name):
        boss_admin_class = site.registry[app_name][model_name]
        query_sets = boss_admin_class.model.objects.all()
        num = query_sets.count()
        query_sets, search_dict = self.get_filter_result(request, query_sets)
        query_sets, ordered_dict = self.get_order_by_result(request, query_sets, boss_admin_class)
        query_sets, search_keyword = self.get_keyword_result(request, query_sets, boss_admin_class)
        boss_admin_class.search_dict = search_dict
        boss_admin_class.search_keyword = search_keyword
        # 分页
        page_obj = MyPager.Pagination(query_sets.count(), request.GET.get('pager', 1))
        query_sets = query_sets[page_obj.start:page_obj.end]
        page_str = page_obj.page_str(request.get_full_path())

        return render(
            request,
            'modeldetail.html',
            {
                'query_sets': query_sets,
                'boss_admin_class': boss_admin_class,
                'model_name': model_name,
                'ordered_dict': ordered_dict,
                'page_str': page_str,
                'num': num
            })

    @method_decorator(login_required)
    def post(self, request, app_name, model_name):
        boss_admin_class = site.registry[app_name][model_name]
        action = request.POST.get('action')
        actionCheckBoxs = json.loads(request.POST.get('checkboxs'))
        quert_sets = boss_admin_class.model.objects.filter(id__in=actionCheckBoxs)
        action_func = getattr(boss_admin_class, action)
        action_func(request, quert_sets)
        return redirect('/bossadmin/%s/%s/'%(app_name, model_name))

    @staticmethod
    def get_filter_result(request, query_sets):
        """
        是否过滤
        :param request:
        :param query_sets:
        :return:
        """
        search_dict = {}
        for k, v in request.GET.items():
            if not v or k in ('o', 'pager', 'Q'):
                continue
            search_dict[k] = v
        return query_sets.filter(**search_dict), search_dict

    @staticmethod
    def get_order_by_result(request, query_sets, boss_admin_class):
        """
        是否根据某个字段排序
        :param request:
        :param query_sets:
        :param boss_admin_class:
        :return:
        """
        ordered_dict = {}
        order_by_index = request.GET.get('o')
        if order_by_index:
            order_by_filed = boss_admin_class.list_display[abs(int(order_by_index))]
            ordered_dict[order_by_filed] = order_by_index
            if order_by_index.startswith('-'):
                order_by_filed = '-{}'.format(order_by_filed)
            query_sets = query_sets.order_by(order_by_filed)
        return query_sets, ordered_dict

    @staticmethod
    def get_keyword_result(request, query_sets, boss_admin_class):
        """
        根据关键字模糊查询
        :param request:
        :param query_sets:
        :param boss_admin_class:
        :return:
        """
        keyword = request.GET.get('Q', '')
        if keyword:
            keyword_search = Q()
            keyword_search.connector = 'OR'
            for search_field in boss_admin_class.search_fields:
                keyword_search.children.append(("%s__contains"% search_field, keyword))
            return query_sets.filter(keyword_search), keyword
        return query_sets, keyword


class ModelRowDataView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ModelRowDataView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, app_name, model_name, nid, status):
        if nid == 'add':
            boss_admin_class, model_form = self.get_data(app_name, model_name, nid)
            form_obj = model_form()
            return render(request, 'modelrowdata.html', locals())
        boss_admin_class, model_form, obj = self.get_data(app_name, model_name, nid)
        if status == 'delete':
            delete_obj = boss_admin_class.model.objects.get(id=nid)
            return render(request, 'modelrowdelete.html', locals())
        form_obj = model_form(instance=obj)
        return render(request, 'modelrowdata.html', locals())

    @method_decorator(login_required)
    def post(self, request, app_name, model_name, nid, status):
        if nid == 'add':
            boss_admin_class, model_form = self.get_data(app_name, model_name, nid)
            form_obj = model_form(data=request.POST)
            if form_obj.is_valid():
                form_obj.save()
                return redirect('/bossadmin/%s/%s/' % (app_name, model_name))
            return render(request, 'modelrowdata.html', {'form_obj': form_obj})
        boss_admin_class, model_form, obj = self.get_data(app_name, model_name, nid)
        if status == 'delete':
            delete_obj = boss_admin_class.model.objects.get(id=nid)
            delete_obj.delete()
            return redirect("/bossadmin/{app_name}/{model_name}/".format(app_name=app_name, model_name=model_name))
        form_obj = model_form(instance=obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/bossadmin/%s/%s/' %(app_name, model_name))
        return render(request, 'modelrowdata.html', locals())

    @staticmethod
    def get_data(app_name, model_name, nid):
        """

        :param app_name: App名称
        :param model_name: 表名称
        :param nid: 编辑的ID
        :return:
        """
        boss_admin_class = site.registry[app_name][model_name]
        if nid == 'add':
            model_form = forms.create_dynamic_form(boss_admin_class, status=True)
            return boss_admin_class, model_form
        model_form = forms.create_dynamic_form(boss_admin_class)
        obj = boss_admin_class.model.objects.filter(id=nid).first()
        return boss_admin_class, model_form, obj