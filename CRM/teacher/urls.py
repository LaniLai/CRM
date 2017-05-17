"""PerfectCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from teacher import views


urlpatterns = [
    url(r'^mycls/$', views.TeacherView.as_view()),
    url(r'^mycls/(\d+)/stu_list/$', views.MyclsStuListView.as_view()),
    url(r'^mycls/add-(\d+)-course-record/$', views.add_course_record),
    url(r'^mycls-(\d+)/$', views.MyclsDetailView.as_view()),

    url(r'^mycls/course-record-(\d+)/roll_call/$', views.MyclsRollCallView.as_view()),
    url(r'^mycls/course-record-(\d+)-json/$', views.MyclsJsonRollCallView.as_view()),
]
