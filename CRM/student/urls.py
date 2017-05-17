

from django.conf.urls import url
from student import views


urlpatterns = [
    url(r'^$', views.StudentView.as_view()),
]
