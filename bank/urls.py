from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('index', views.index, name='index'),
    path('create_corporation', views.create_corporation, name='create_corporation'),
    path('create_bank', views.create_bank, name='create_bank'),
    path('hire_employee', views.hire_employee, name='hire_employee'),
    path('replace_manager', views.replace_manager, name='replace_manager'),
    path('account_withdrawal', views.account_withdrawal, name='account_withdrawal'),
    
    
    # Screens 3, 4, 5, (Queries 3-6)
    path('create_employee_role', views.create_employee_role, name='(3) create_employee_role'),
    path('create_customer_role', views.create_customer_role, name='(4) create_customer_role'),
    path('stop_employee_and_customer_role', views.stop_employee_and_customer_role, name='(5) stop employee/customer role'),    
    # # Screen 7, Query 11
    path('create_fee', views.create_fee, name='(11) create_fee'),
]