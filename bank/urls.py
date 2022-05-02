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
    path(
        "start_overdraft",
        views.start_overdraft,
        name="start_overdraft",
    ),
    path(
        "stop_overdraft",
        views.stop_overdraft,
        name="stop_overdraft",
    ),
    path(
        "account_deposit",
        views.account_deposit,
        name="account_deposit",
    ),
    path(
        "account_transfer",
        views.account_transfer,
        name="account_transfer",
    ),
    path("", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("index", views.index, name="index"),
    path("create_corporation", views.create_corporation, name="create_corporation"),
    path("create_bank", views.create_bank, name="create_bank"),
    path("hire_employee", views.hire_employee, name="hire_employee"),
    path("replace_manager", views.replace_manager, name="replace_manager"),
    path("account_withdrawal", views.account_withdrawal, name="account_withdrawal"),
]
