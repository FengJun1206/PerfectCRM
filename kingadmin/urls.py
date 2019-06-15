from django.urls import path, re_path
from kingadmin import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('sales_dashboard/', views.sales_dashboard, name='sales_dashboard'),

    re_path(r'^(\w+)/(\w+)/$', views.table_obj_list, name='table_obj_list'),
    re_path(r'^(\w+)/(\w+)/(\d+)/change/$', views.table_obj_change, name='table_obj_change'),
    re_path(r'^(\w+)/(\w+)/add/$', views.table_obj_add, name='table_obj_add'),
    re_path(r'^(\w+)/(\w+)/(\d+)/delete/$', views.table_obj_delete, name='table_obj_delete'),

    re_path(r'^(\w+)/$', views.app_manager, name='app_manager'),

    path('login/', views.acc_login, name='login'),
    path('logout/', views.acc_logout, name='logout'),
]
