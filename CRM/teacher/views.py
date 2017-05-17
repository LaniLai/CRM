from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from repository import models
from teacher.service import forms
from teacher.service.response import BaseResponse
import json


class TeacherView(View):
    """ 讲师对应管理的班级 """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TeacherView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        my_class = models.ClassList.objects.filter(teachers=request.user)
        return render(request, 'teacher/mycls.html', {'my_class': my_class})


class MyclsStuListView(View):
    """ 班级对应的学员列表 """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MyclsStuListView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, cls_id):
        cls_obj = models.ClassList.objects.filter(id=cls_id).first()
        stu_list = cls_obj.student_set.all()
        return render(
            request,
            'teacher/cls_stu_list.html',
            {
                'stu_list': stu_list,
                'cls_obj': cls_obj
            }
        )


class MyclsDetailView(View):
    """ 班级详细(上课记录) """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MyclsDetailView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, cls_id):
        """
        根据班级展示该班下所有上课记录
        :param request:
        :param cls_id:
        :return:
        """
        course_record_list = models.CourseRecord.objects.filter(class_grade_id=cls_id)
        return render(request, 'teacher/cls_record_list.html', locals())

    @method_decorator(login_required)
    def post(self, request, cls_id):
        """
        初始化上课记录的所有学习记录
        :param request:
        :param cls_id:
        :return:
        """
        course_record_list = models.CourseRecord.objects.filter(class_grade_id=cls_id)
        action = request.POST.get('action')
        courserecord_id = request.POST.get('courserecord_id')   # 对应的某条上课记录ID
        action_func = getattr(self, action)
        result = action_func(request, courserecord_id, cls_id)
        if not result:
            return render(request, 'teacher/cls_record_list.html',
                          {
                              'error_msg': '初始化学习记录失败, 检查该节课是否对应的学习记录',
                              'course_record_list': course_record_list
                          })
        else:
            # 初始化成功, 跳转到点名页
            return redirect(
                '/teacher/mycls/course-record-{0}/roll_call'.format(courserecord_id)
            )

    @staticmethod
    def initialization_studyRecord(request, courserecord_id, cls_id):
        """
        初始化该上课记录的学习记录
        根据班级ID反查对应的所有学生
        :param request:
        :param courserecord_id: 对应的某条上课记录ID
        :param cls_id: 班级ID
        :return:
        """
        cls_obj = models.ClassList.objects.get(id=cls_id)
        cls_record_obj = models.CourseRecord.objects.get(id=courserecord_id)
        cls_stu_list = models.Student.objects.filter(class_grades=cls_obj)
        new_study_record_list = []
        for stu in cls_stu_list:
            new_study_record_list.append(models.StudyRecord(
                course_record=cls_record_obj,
                student=stu,
                score=0,
                show_status=1,
            ))
        try:
            models.StudyRecord.objects.bulk_create(new_study_record_list)
            return True
        except Exception:
            return False


class MyclsRollCallView(View):
    """
    上课记录对应点名视角
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MyclsRollCallView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, course_record_id):
        """
        根据上课记录过滤出匹配的所有的学习记录
        :param request:
        :param course_record_id: 上课记录ID
        :return:
        """
        course_record_obj = models.CourseRecord.objects.get(id=course_record_id)
        return render(request, 'teacher/cls_roll_call.html', {'course_record_obj': course_record_obj})


class MyclsJsonRollCallView(View):
    """ Ajax获取上课记录对应的学习记录 """
    @method_decorator(login_required)
    def get(self, request, course_record_id):
        """
        动态获取 上课记录对应的所有学习记录
        :param request:
        :param course_record_id: 上课记录ID
        :return:
        """
        table_config, show_list = self.get_table_config()
        study_record_list = \
            models.StudyRecord.objects.filter(course_record_id=course_record_id).values(*show_list)
        study_record_list = list(study_record_list)
        result = {
            'table_config': table_config,
            'data_list': study_record_list,
            'global_dict': {
                'score_choices': models.StudyRecord.score_choices,
                'show_choices': models.StudyRecord.show_choices,
            },
        }
        return HttpResponse(json.dumps(result))

    @method_decorator(csrf_exempt)
    def put(self, request, course_record_id):
        response = BaseResponse()
        response.error = []
        error_count = 0
        put_dict = json.loads(str(request.body, encoding='utf-8'))
        for row_dict in put_dict:
            nid = row_dict.pop('id')
            try:
                models.StudyRecord.objects.filter(id=nid).update(**row_dict)
            except Exception as e:
                response.error.append({'nid': nid, 'message': str(e)})
                response.status = False
                error_count += 1
        if error_count:
            response.message = '共%s条,失败%s条' % (len(put_dict), error_count,)
        else:
            response.message = '更新成功'
        return HttpResponse(json.dumps(response.__dict__))

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
                'q': 'student__customer__name',
                'title': '名字',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@student__customer__name"}},
                'attrs': {}
            },
            {
                'q': 'show_status',
                'title': '考勤',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@@show_choices"}},
                'attrs': {'name': 'show_status', 'origin': "@show_status", 'edit-enable': 'true',
                          'edit-type': 'select', "global-name": 'show_choices'}
            },
            {
                'q': 'score',
                'title': '本节成绩',
                'display': True,
                'text': {'content': "{n}", 'kwargs': {'n': "@@score_choices"}},
                'attrs': {'name': 'score', 'origin': "@score", 'edit-enable': 'true',
                          'edit-type': 'select', "global-name": 'score_choices'}
            },
            {
                'q': None,
                'title': '操作',
                'display': True,
                'text': {'content': '{m}', 'kwargs': {'m': '查看详细'}},
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


@method_decorator(csrf_exempt)
def add_course_record(request, cls_id):
    """
    添加上课记录
    :param request:
    :param cls_id: 上课班级ID
    :return:
    """
    cls_obj = models.ClassList.objects.filter(id=cls_id).first()
    cls_form = forms.AddClsRecordForm(instance=cls_obj)
    if request.method == 'POST':
        cls_form = forms.AddClsRecordForm(instance=cls_obj, data=request.POST)
        if cls_form.is_valid():
            # cls_form.instance.save()
            models.CourseRecord.objects.create(**cls_form.cleaned_data)
            return redirect('/teacher/mycls-{0}/'.format(cls_id))
    return render(request, 'teacher/cls_add_record.html', locals())