from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.utils.timezone import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django import conf
from repository import models
from BossAdmin.utlis import MyPager
from crm.service import forms
from crm.service import sendEmail
import random, string, json, os


class SaleIndexView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SaleIndexView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, 'crm/my_customer.html')


class SaleJsonView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SaleJsonView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        table_config, show_list = self.get_table_config()
        current_pager = request.GET.get('pager', 1)
        page_obj = MyPager.Pagination\
            (models.CustomerInfo.objects.filter(consultant=request.user).count(), currentPage=current_pager)
        page_str = page_obj.page_str('javascript:void(0);')
        customers = models.CustomerInfo.objects.\
            filter(consultant=request.user).order_by('status').values(*show_list)[page_obj.start:page_obj.end]
        customers = list(customers)
        result = {
            'table_config': table_config,
            'data_list': customers,
            'global_dict': {
                'contact_type_choices': models.CustomerInfo.contact_type_choices,
                'source_choices': models.CustomerInfo.source_choices,
                'status_choices': models.CustomerInfo.status_choices
            },
            'pager': page_str
        }
        return HttpResponse(json.dumps(result))

    @staticmethod
    def get_table_config():
        table_config = [
            {
                'q': None,
                'title': "选项",
                'display': True,
                'text': {'content': "<input type='checkbox' />", "kwargs": {}},
                'attrs': {}
            },
            {
                'q': 'id',
                'title': 'ID',
                'display': False,
                'text': {},
                'attrs': {}
            },
            {
                'q': 'name',
                'title': '名字',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@name"}},
                'attrs': {}
            },
            {
                'q': 'contact_type',
                'title': '联系来源',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@@contact_type_choices"}},
                'attrs': {}
            },
            {
                'q': 'contact',
                'title': '联系方式',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@contact"}},
                'attrs': {}
            },
            {
                'q': 'source',
                'title': '客户来源',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@@source_choices"}},
                'attrs': {}
            },
            {
                'q': 'referral_from__name',
                'title': '转介绍人',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@referral_from__name"}},
                'attrs': {}
            },
            {
                'q': 'status',
                'title': '状态',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@@status_choices"}},
                'attrs': {}
            },
            {
                'q': None,
                'title': '操作',
                'display': True,
                'text': {'content': "<a href='/crm/stu_enrollment-{m}/'>{n}</a>", 'kwargs': {'n': '报名', 'm': '@id'}},
                'attrs': {},
            }
        ]
        # 多对多Bug
        q_list = []
        for i in table_config:
            if not i['q']:
                continue
            q_list.append(i['q'])
        return table_config, q_list


class StuEnrollment(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StuEnrollment, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, nid):
        customer_obj = models.CustomerInfo.objects.filter(id=nid, status=0).first()
        class_lists = models.ClassList.objects.all()
        return render(request, 'crm/stu_enrollment.html',
                      {
                          'customer': customer_obj,
                          'class_lists': class_lists
                       })

    @method_decorator(login_required)
    def post(self, request, nid):
        pass

    @method_decorator(login_required)
    def patch(self, request, customer_id):
        """
        生成报名链接交给用户填写并创建报名记录
        :param request:
        :param nid:
        :return:
        """
        msg = {'status': True, 'code': '200', 'enrollment_link': None, 'enrollment_id': None}
        # 根据状态码去调控

        class_grade_id = json.loads(str(request.body, encoding='utf8')).get('class_grade_id')
        try:
            enrollment_obj = models.StudentEnrollment.objects.create(
                customer_id=customer_id,
                class_grade_id=class_grade_id,
                consultant_id=request.user.userprofile.id,
            )
        except Exception as e:
            # 创建报名表链接成功
            enrollment_obj = models.StudentEnrollment.objects.get(customer_id=customer_id,
                                class_grade_id=class_grade_id,)
            if enrollment_obj.contract_agreed:
                # 如果合同通过
                msg.update(
                    {'enrollment_link': '等待客户填写进行审核...', 'code': '201', 'enrollment_id':enrollment_obj.id}
                )
                return HttpResponse(json.dumps(msg))
        random_str = ''.join(random.sample(string.ascii_lowercase+string.digits, 8))
        enrollment_link = "http://localhost:8000/crm/registration-{0}/{1}.html".format(enrollment_obj.id, random_str)
        cache.set(customer_id, random_str, 3600)
        msg.update({'enrollment_link': enrollment_link, 'enrollment_id': enrollment_obj.id})
        return HttpResponse(json.dumps(msg))


class StuContractAudit(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StuContractAudit, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, enroll_id):
        enrollment_obj = models.StudentEnrollment.objects.get(id=enroll_id)
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
        enrollment_form = forms.EnrollmentForm(instance=enrollment_obj)
        return render(request, 'crm/contract_audit.html', locals())

    @method_decorator(login_required)
    def post(self, request, enroll_id):
        enrollment_obj = models.StudentEnrollment.objects.get(id=enroll_id)
        enrollment_form = forms.EnrollmentForm(instance=enrollment_obj, data=request.POST)
        if enrollment_form.is_valid():
            enrollment_form.save()
            stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)[0]
            stu_obj.class_grades.add(enrollment_obj.class_grade_id)
            stu_obj.save()
            enrollment_obj.customer.status = 1
            enrollment_obj.customer.save()
            # 发送邮件
            result = self.send_email(enrollment_obj.customer)
            if result:
                enrollment_obj.contract_approved = True
                enrollment_obj.save()
                return HttpResponse('报名成功')
            else:
                return HttpResponse('邮件发送失败！！！')
        return render(request, 'crm/contract_audit.html', locals())

    @staticmethod
    def send_email(customer_obj):
        return sendEmail.initialization(customer_obj)


@method_decorator(csrf_exempt)
def registration(request, enroll_id, random_str):
    """
    报名表填写
    :param request:
    :param enroll_id: 注册id
    :param random_str: 随机字符串
    :return:
    """
    enrollment_obj = models.StudentEnrollment.objects.get(id=enroll_id)
    if enrollment_obj.contract_agreed:
        if enrollment_obj.contract_approved:
            return HttpResponse(
                '欢迎加入老男孩,合同审核通过, 并为您的邮箱发送了一封邮件已便于交作业和查看成绩'
            )
        return HttpResponse("报名合同正在审核中....")
    if request.method == 'GET':
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
    elif request.method == "POST":
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer, data=request.POST)
        if customer_form.is_valid():
            customer_form.save()
            enrollment_obj.contract_agreed = True
            enrollment_obj.contract_signed_date = datetime.now()
            enrollment_obj.save()
            return HttpResponse("您已成功提交报名信息,请等待审核通过...")

    uploaded_files = []
    enrollment_upload_path = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enroll_id)
    if os.path.isdir(enrollment_upload_path):
        uploaded_files = os.listdir(enrollment_upload_path)

    return render(request, 'crm/registration.html', locals())
    # if cache.get(enroll_id) == random_str:
    # else:
    #     return HttpResponse('该链接已失效')


@method_decorator(csrf_exempt)
def stu_file_upload(request, enroll_id):
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enroll_id)
    if not os.path.isdir(enrollment_upload_dir):
        os.mkdir(enrollment_upload_dir)
    file_obj = request.FILES.get('file')
    print(file_obj)
    if len(os.listdir(enrollment_upload_dir)) <= 2:
        with open(os.path.join(enrollment_upload_dir, file_obj.name), "wb") as f:
            for chunks in file_obj.chunks():
                f.write(chunks)
    else:
        return HttpResponse(json.dumps({'status': False, 'err_msg': '文件数量已达到上限'}))
    return HttpResponse(json.dumps({'status': True}))