from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class StudentView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """ 我的班级列表 """
        return render(request, 'student/my_grade.html')
