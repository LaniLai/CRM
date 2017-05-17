

from django.conf.urls import url
from crm import views

urlpatterns = [
    url(r'customers/$', views.SaleIndexView.as_view()),
    url(r'customers-json/$', views.SaleJsonView.as_view()),
    url(r'stu_enrollment-(\d+)/$', views.StuEnrollment.as_view()),
    url(r'stu_enrollment/(\d+)/fileupload/$', views.stu_file_upload,name="stu_enrollment_fileupload"),
    url(r'stu_enrollment/(\d+)/contract_audit/$', views.StuContractAudit.as_view()),

    url(r'registration-(\d+)/(\w+).html$', views.registration),
]
