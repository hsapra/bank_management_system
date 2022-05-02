from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_corporation', views.create_corporation, name='create_corporation'),
    path('create_bank', views.create_bank, name='create_bank'),
    path('display_account_stats', views.display_account_stats, name='display_account_stats'),
    path('display_bank_stats', views.display_bank_stats, name='display_bank_stats'),
    path('display_corporation_stats', views.display_corporation_stats, name='display_corporation_stats'),
    path('display_customer_stats', views.display_customer_stats, name='display_customer_stats'),
    path('display_employee_stats', views.display_employee_stats, name='display_employee_stats'),
]