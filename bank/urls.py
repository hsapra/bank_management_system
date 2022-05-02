from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_corporation", views.create_corporation, name="create_corporation"),
    path("create_bank", views.create_bank, name="create_bank"),
    path(
        "remove_account_access",
        views.remove_account_access,
        name="remove_account_access",
    ),
]
