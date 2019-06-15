from django.urls import path, re_path
from crm import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='sales_dashboard'),
    path('student_enrollment/', views.student_enrollment, name='student_enrollment'),
    re_path(r'^enrollment/(\d+)/$', views.enrollment, name='enrollment'),
    re_path(r'^enrollment/(\d+)/fielupload/$', views.enrollment_fileupload, name='enrollment_fileupload'),

    re_path(r'^student_enrollment/(\d+)/contract_audit/$', views.contract_audit, name='contract_audit'),

]
