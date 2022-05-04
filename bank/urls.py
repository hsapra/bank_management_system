from django.urls import path

from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("index", views.index, name="index"),
    path("pay_employees", views.pay_employees, name="pay_employees"),
    # path('admin_home', views.admin_home, name='admin_home'),
    # path('manager_home', views.manager_home, name='manager_home'),
    # path('customer_home', views.customer_home, name='customer_home'),
    path("create_corporation", views.create_corporation, name="create_corporation"),
    path("create_bank", views.create_bank, name="create_bank"),
    path(
        "display_account_stats",
        views.display_account_stats,
        name="display_account_stats",
    ),
    path("display_bank_stats", views.display_bank_stats, name="display_bank_stats"),
    path(
        "display_corporation_stats",
        views.display_corporation_stats,
        name="display_corporation_stats",
    ),
    path(
        "display_customer_stats",
        views.display_customer_stats,
        name="display_customer_stats",
    ),
    path(
        "display_employee_stats",
        views.display_employee_stats,
        name="display_employee_stats",
    ),
    path("hire_employee", views.hire_employee, name="hire_employee"),
    path("replace_manager", views.replace_manager, name="replace_manager"),
    path("account_withdrawal", views.account_withdrawal, name="account_withdrawal"),
    path(
        "manage_accounts",
        views.manage_accounts,
        name="manage_accounts",
    ),
    path(
        "remove_account_access",
        views.remove_account_access,
        name="remove_account_access",
    ),
    path(
        "add_account_access",
        views.add_account_access,
        name="add_account_access",
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
    path(
        "create_employee_role",
        views.create_employee_role,
        name="(3) create_employee_role",
    ),
    path(
        "create_customer_role",
        views.create_customer_role,
        name="(4) create_customer_role",
    ),
    path(
        "stop_employee_and_customer_role",
        views.stop_employee_and_customer_role,
        name="(5) stop employee/customer role",
    ),
    path("create_fee", views.create_fee, name="(11) create_fee"),
]
