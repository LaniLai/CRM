
from django.conf.urls import url

from BossAdmin.views import account
from BossAdmin.views import home

urlpatterns = [
    url(r'^$', home.IndexView.as_view()),
    url(r'^logout/$', account.LogoutView.as_view()),
    url(r'^login/$', account.LoginView.as_view()),
    url(r'^(\w+)/(\w+)/$', home.ModelDetailView.as_view(), name='TableDetail'),
    url(r'^(\w+)/(\w+)/(\d+|add)/(change|delete)?/?', home.ModelRowDataView.as_view(), name='action'),
]
