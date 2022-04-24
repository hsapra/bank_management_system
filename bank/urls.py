from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_corporation', views.create_corporation, name='create_corporation'),
    path('create_bank', views.create_bank, name='create_bank'),
]