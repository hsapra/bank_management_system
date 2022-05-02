from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_corporation', views.create_corporation, name='(1) create_corporation'),
    path('create_bank', views.create_bank, name='(2) create_bank'),
    # path('result_view', views.result_view, name='result_view'),
    
    # Screens 3, 4, 5, (Queries 3-6)
    path('create_employee_role', views.create_employee_role, name='(3) create_employee_role'),
    path('create_customer_role', views.create_customer_role, name='(4) create_customer_role'),
    path('stop_employee_and_customer_role', views.stop_employee_and_customer_role, name='(5) stop employee/customer role'),
    # path('hire_worker', views.hire_worker, name="(6) hire worker"),
    
    # Screen 7, Query 11
    path('create_fee', views.create_fee, name='(11) create_fee'),
    
]