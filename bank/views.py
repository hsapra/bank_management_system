from django.shortcuts import render, redirect
import importlib
import math
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast

# Create your views here.
from .forms import CreateCorporationForm, CreateBankForm
from bank.models import *
from django.contrib import messages
import datetime


# Create your views here.
from .forms import *
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.db import IntegrityError
from psycopg2.errorcodes import UNIQUE_VIOLATION


def get_url_names():
    from django.apps import apps

    list_of_url_names = list()
    list_of_all_urls = list()
    for name, app in apps.app_configs.items():
        mod_to_import = f"{name}.urls"
        try:
            urls = getattr(importlib.import_module(mod_to_import), "urlpatterns")
            list_of_all_urls.extend(urls)
        except ImportError as ex:
            # is an app without urls
            pass
    for url in list_of_all_urls:
        list_of_url_names.append((url.name, url.pattern))

    return list_of_url_names


def get_Accounts():
    list_of_accts = list(
        BankAccount.objects.all().values_list("accountid", flat=True).distinct()
    )

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)]

    tuple_list = []

    for acct in list_of_accts:
        tuple_list.append((acct, acct))

    return tuple_list


def get_Persons():
    list_of_people = list(
        Person.objects.all().values_list("perid", flat=True).distinct()
    )

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)]

    tuple_list = []

    for people in list_of_people:
        tuple_list.append((people, people))

    return tuple_list


def get_Corporations():
    print("Called Corp")
    list_of_corps = list(
        Corporation.objects.all().values_list("corpid", flat=True).distinct()
    )

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)]

    tuple_list = []

    for corps in list_of_corps:
        tuple_list.append((corps, corps))

    return tuple_list


def get_Employees():
    list_of_emps = list(
        Employee.objects.all().values_list("perid", flat=True).distinct()
    )

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)]

    tuple_list = []

    for emp in list_of_emps:
        tuple_list.append((emp, emp))

    return tuple_list


def get_Banks():
    list_of_banks = list(Bank.objects.all().values_list("bankid", flat=True).distinct())

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)]

    tuple_list = []

    for bank in list_of_banks:
        tuple_list.append((bank, bank))

    return tuple_list


def get_Customers():
    list_of_banks = list(
        Customer.objects.all().values_list("perid", flat=True).distinct()
    )

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)]

    tuple_list = []

    for bank in list_of_banks:
        tuple_list.append((bank, bank))

    return tuple_list


def get_Bank_users():
    list_of_bank_users = list(
        BankUser.objects.all().values_list("perid", flat=True).distinct()
    )

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)]

    tuple_list = []

    for perid in list_of_bank_users:
        tuple_list.append((perid, perid))

    return tuple_list


def is_checking(bankID, accountID):
    return len(Checking.objects.filter(bankid=bankID, accountid=accountID)) > 0


###### VIEWS ##########


def login(request):
    if "perID" in request.session and request.session["perID"]:
        return index(request)

    else:
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                perID = form.cleaned_data["perID"]
                pwd = form.cleaned_data["pwd"]

                if len(Person.objects.filter(pk=perID)) == 0:
                    messages.error(request, "Invalid Username")
                elif Person.objects.get(pk=perID).pwd != pwd:
                    messages.error(request, "Invalid Password")
                else:
                    messages.success(request, "Logged In")
                    request.session["perID"] = perID
                    request.session["isCustomer"] = (
                        len(Customer.objects.filter(pk=perID)) != 0
                    )
                    request.session["isAdmin"] = (
                        len(SystemAdmin.objects.filter(pk=perID)) != 0
                    )
                    request.session["isManager"] = (
                        len(Bank.objects.filter(manager_id=perID)) != 0
                    )
                    return index(request)
        else:
            form = LoginForm()
        return render(request, "bank/login.html", {"form": form})


def logout(request):
    if "perID" in request.session:
        perID = request.session.pop("perID")
    return redirect("/bank/")


@never_cache
def index(request):
    cache.clear()
    if "perID" in request.session and request.session["perID"]:
        if request.session["isAdmin"]:
            return admin_home(request)
        elif request.session["isManager"]:
            return manager_home(request)
        elif request.session["isCustomer"]:
            return customer_home(request)
        else:
            role = "Employee/Person"
        return customer_home(request)
    else:
        messages.error(
            request, "Access Denied. Please Log In with the correct credentials"
        )
        return redirect("/bank/")


@never_cache
def admin_home(request):
    cache.clear()
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and request.session["isAdmin"]
    ):
        return render(
            request,
            "bank/admin_home.html",
            {"perID": request.session["perID"], "role": "Admin"},
        )
    else:
        messages.error(
            request, "Access Denied. Please Log In with the correct credentials"
        )
        return redirect("/bank/")


@never_cache
def manager_home(request):
    cache.clear()
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and request.session["isManager"]
    ):
        return render(
            request,
            "bank/manager_home.html",
            {"perID": request.session["perID"], "role": "Manager"},
        )
    else:
        messages.error(
            request, "Access Denied. Please Log In with the correct credentials"
        )
        return redirect("/bank/")


@never_cache
def customer_home(request):
    cache.clear()
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and request.session["isCustomer"]
    ):
        return render(
            request,
            "bank/customer_home.html",
            {"perID": request.session["perID"], "role": "Customer"},
        )
    else:
        messages.error(
            request, "Access Denied. Please Log In with the correct credentials"
        )
        return redirect("/bank/")


@never_cache
def manage_accounts(request):
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isCustomer"] or request.session["isAdmin"])
    ):
        return render(request, "bank/manage_accounts.html")
    else:
        messages.error(
            request, "Access Denied. Please Log In with the correct credentials"
        )
        return redirect("/bank/")


##### QUERIES ##############


#### Query 1
@never_cache
def create_corporation(request):
    cache.clear()
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = CreateCorporationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if (
                len(Corporation.objects.filter(corpid=form.cleaned_data["corpID"])) != 0
                or len(
                    Corporation.objects.filter(shortname=form.cleaned_data["shortName"])
                )
                != 0
                or len(
                    Corporation.objects.filter(longname=form.cleaned_data["longName"])
                )
                != 0
            ):
                messages.error(request, "Data Exists.")
            else:
                new_corp = Corporation(
                    corpid=form.cleaned_data["corpID"],
                    shortname=form.cleaned_data["shortName"],
                    longname=form.cleaned_data["longName"],
                    resassets=form.cleaned_data["resAssets"],
                )
                new_corp.save()
                messages.success(request, "Corporation Created Successfully!")
        else:
            messages.error(request, "Invalid form submission.")
            messages.error(request, form.errors)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreateCorporationForm()

    context = {"form": form}

    return render(request, "bank/create_corporation.html", context)


#### Query 2
@never_cache
def create_bank(request):
    cache.clear()
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = CreateBankForm(
            request.POST, corporations=get_Corporations(), employees=get_Employees()
        )
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if len(Bank.objects.filter(manager_id=form.cleaned_data["manager"])) == 0:
                if (
                    len(
                        Bank.objects.filter(
                            manager_id=form.cleaned_data["bank_employee"]
                        )
                    )
                    == 0
                ):
                    if (
                        len(Bank.objects.filter(bankid=form.cleaned_data["bankID"]))
                        == 0
                    ):
                        new_bank = Bank(
                            bankid=form.cleaned_data["bankID"],
                            bankname=form.cleaned_data["bankName"],
                            street=form.cleaned_data["street"],
                            city=form.cleaned_data["city"],
                            state=form.cleaned_data["state"],
                            zip=form.cleaned_data["zip_code"],
                            resassets=form.cleaned_data["resAssets"],
                            corpid=Corporation.objects.get(
                                pk=form.cleaned_data["corpID"]
                            ),
                            manager=Employee.objects.get(
                                pk=form.cleaned_data["manager"]
                            ),
                        )
                        new_bank.save()
                        work_for_employee, created = Workfor.objects.get_or_create(
                            bankid=new_bank,
                            perid=Employee.objects.get(
                                pk=form.cleaned_data["bank_employee"]
                            ),
                        )

                        if created:
                            messages.success(request, "Bank Created Successfully!")
                        else:
                            messages.error(
                                request, "Failed to create Employee-Bank Relation"
                            )
                    else:
                        messages.error(request, "Existing Bank.")
                else:
                    messages.error(request, "Employee cannot be existing manager.")
            else:
                messages.error(request, "Manager cannot be existing manager.")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreateBankForm(
            corporations=get_Corporations(), employees=get_Employees()
        )

    return render(request, "bank/create_bank.html", {"form": form})


### Query 3
@never_cache
def create_employee_role(request):
    if request.method == "POST":
        form = CreateEmployeeRoleForm(request.POST, persons=get_Persons())
        if form.is_valid():

            if (
                len(Employee.objects.filter(perid=form.cleaned_data["perID"])) == 0
                and len(SystemAdmin.objects.filter(perid=form.cleaned_data["perID"]))
                == 0
            ):
                new_employee_role = Employee(
                    perid=BankUser.objects.get(pk=form.cleaned_data["perID"]),
                    salary=form.cleaned_data["salary"],
                    payments=form.cleaned_data["payments"],
                    earned=form.cleaned_data["earned"],
                )
                new_employee_role.save()

                messages.success(request, "Employee Role Started")
            else:
                messages.error(
                    request, "Cannot start customer role for existing employee/admin"
                )
    else:
        form = CreateEmployeeRoleForm(persons=get_Persons())
    return render(request, "bank/create_employee_role.html", {"form": form})

    ### Query 4


@never_cache
def create_customer_role(request):
    if request.method == "POST":
        form = CreateCustomerRoleForm(request.POST, perid=get_Persons())
        if form.is_valid():

            if (
                len(SystemAdmin.objects.filter(perid=form.cleaned_data["perID"])) == 0
                and len(Customer.objects.filter(perid=form.cleaned_data["perID"])) == 0
            ):
                new_customer = Customer(
                    perid=BankUser.objects.get(pk=form.cleaned_data["perID"]),
                )
                new_customer.save()

                messages.success(request, "Customer Role Started")
            else:
                messages.error(
                    request, "Cannot start customer role for existing customer/admin"
                )
    form = CreateCustomerRoleForm(perid=get_Persons())

    return render(request, "bank/create_customer_role.html", {"form": form})


### Query 5/6
@never_cache
def stop_employee_and_customer_role(request):
    if request.method == "POST":
        form1 = StopEmployeeRoleForm(request.POST, employee=get_Employees())
        form2 = StopCustomerRoleForm(request.POST, customer=get_Customers())
        if "employee" in request.POST and form1.is_valid():
            if len(Employee.objects.filter(perid=form1.cleaned_data["perID"])) >= 1:
                employee_bank_ids = Workfor.objects.filter(
                    perid=form1.cleaned_data["perID"]
                ).values_list("bankid", flat=True)
                can_happen = True
                for bank_id in employee_bank_ids:
                    if len(Workfor.objects.filter(bankid=bank_id)) == 1:
                        can_happen = False
                if can_happen:
                    if (
                        len(Bank.objects.filter(manager_id=form1.cleaned_data["perID"]))
                        == 0
                    ):
                        Workfor.objects.filter(
                            perid=form1.cleaned_data["perID"]
                        ).delete()
                        Employee.objects.filter(
                            perid=form1.cleaned_data["perID"]
                        ).delete()

                        if (
                            len(
                                Customer.objects.filter(
                                    perid=form1.cleaned_data["perID"]
                                )
                            )
                            == 0
                        ):
                            BankUser.objects.filter(
                                perid=form1.cleaned_data["perID"]
                            ).delete()
                            Person.objects.filter(
                                perid=form1.cleaned_data["perID"]
                            ).delete()

                        messages.success(request, "Employee Role Stopped")
                    else:
                        messages.error(request, "Manager cannot be removed")
                else:
                    messages.error(request, "1 employee needs to work at the bank")
            else:
                messages.error(request, "Person is an admin or not an employee")

        if "customer" in request.POST and form2.is_valid():
            customer_accessed_accounts = Access.objects.filter(
                perid=form2.cleaned_data["perID"]
            ).values_list("bankid", "accountid")
            can_happen = True
            for bank, account in customer_accessed_accounts:
                if len(Access.objects.filter(bankid=bank, accountid=account)) == 1:
                    can_happen = False
            if can_happen:
                if len(Employee.objects.filter(perid=form2.cleaned_data["perID"])) > 0:
                    Access.objects.filter(perid=form2.cleaned_data["perID"]).delete()
                    CustomerContacts.objects.filter(
                        perid=form2.cleaned_data["perID"]
                    ).delete()
                    Customer.objects.filter(perid=form2.cleaned_data["perID"]).delete()
                else:
                    Access.objects.filter(perid=form2.cleaned_data["perID"]).delete()
                    CustomerContacts.objects.filter(
                        perid=form2.cleaned_data["perID"]
                    ).delete()
                    Customer.objects.filter(perid=form2.cleaned_data["perID"]).delete()
                    BankUser.objects.filter(perid=form2.cleaned_data["perID"]).delete()
                    Person.objects.filter(perid=form2.cleaned_data["perID"]).delete()
                messages.success(request, "Customer Role Stopped")
            else:
                messages.error(
                    request, "Customer is connected to an account as a sole owner"
                )
    form1 = StopEmployeeRoleForm(employee=get_Employees())
    form2 = StopCustomerRoleForm(customer=get_Customers())

    return render(
        request,
        "bank/stop_employee_and_customer_role.html",
        {"form1": form1, "form2": form2},
    )


# Query 7
@never_cache
def hire_employee(request):
    cache.clear()
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = HireEmployeeForm(
            request.POST, employees=get_Employees(), banks=get_Banks()
        )
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if len(Bank.objects.filter(manager_id=form.cleaned_data["perID"])) == 0:
                work_for_employee, created = Workfor.objects.get_or_create(
                    bankid=Bank.objects.get(pk=form.cleaned_data["bankID"]),
                    perid=Employee.objects.get(pk=form.cleaned_data["perID"]),
                )
                if created is True:
                    messages.success(request, "Employee Hired!")
                else:
                    messages.error(request, "Key already exists.")
                employee = Employee.objects.filter(
                    pk=form.cleaned_data["perID"]
                ).update(salary=form.cleaned_data["salary"])
            else:
                messages.error(request, "Employee cannot be existing manager.")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HireEmployeeForm(employees=get_Employees(), banks=get_Banks())

    return render(request, "bank/hire_employee.html", {"form": form})


# Query 8
@never_cache
def replace_manager(request):
    cache.clear()
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = ReplaceManagerForm(
            request.POST, employees=get_Employees(), banks=get_Banks()
        )
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if len(Bank.objects.filter(manager_id=form.cleaned_data["perID"])) == 0:
                if len(Workfor.objects.filter(perid=form.cleaned_data["perID"])) == 0:
                    bank = Bank.objects.filter(pk=form.cleaned_data["bankID"]).update(
                        manager=Employee.objects.get(pk=form.cleaned_data["perID"])
                    )
                    employee = Employee.objects.filter(
                        pk=form.cleaned_data["perID"]
                    ).update(salary=form.cleaned_data["salary"])
                    messages.success(request, "Manager Replaced!")
                else:
                    messages.error(request, "Employee cannot be existing worker.")
            else:
                messages.error(request, "Employee cannot be existing manager.")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ReplaceManagerForm(employees=get_Employees(), banks=get_Banks())

    return render(request, "bank/replace_manager.html", {"form": form})


# Query 9
def add_account_access(request):
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and request.session["isAdmin"]
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form1 = AddAccountForm(
                request.POST, customers=get_Customers(), banks=get_Banks()
            )
            form2 = AddAccountAccessForm(
                request.POST,
                customers=get_Customers(),
                banks=get_Banks(),
                accounts=get_Accounts(),
            )
            # check whether it's valid:
            if "add" in request.POST and form1.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                bankAcct, bankAcct_created = BankAccount.objects.get_or_create(
                    bankid=Bank.objects.get(pk=form1.cleaned_data["bankID"]),
                    accountid=form1.cleaned_data["accountID"],
                    balance=form1.cleaned_data["initialBalance"],
                )
                if not bankAcct_created:
                    messages.error(request, "Account already exists")
                else:
                    now = datetime.datetime.now()
                    access, access_created = Access.objects.get_or_create(
                        bankid=bankAcct,
                        accountid=bankAcct.accountid,
                        perid=Customer.objects.get(pk=form1.cleaned_data["customerID"]),
                        dtsharestart=now,
                    )
                    accountType = form1.cleaned_data["accountType"]
                    if accountType == "Checking":
                        checking, _ = Checking.objects.get_or_create(
                            bankid=bankAcct,
                            accountid=bankAcct.accountid,
                        )
                    elif accountType == "Savings":
                        interest, _ = InterestBearing.objects.get_or_create(
                            bankid=bankAcct,
                            accountid=bankAcct.accountid,
                        )
                        InterestBearing.objects.filter(
                            bankid=bankAcct,
                            accountid=bankAcct.accountid,
                        ).update(
                            interest_rate=form1.cleaned_data["interestRate"],
                            dtdeposit=now,
                        )
                        savings, _ = Savings.objects.get_or_create(
                            bankid=interest, accountid=interest.accountid
                        )
                        Savings.objects.filter(
                            bankid=interest, accountid=interest.accountid
                        ).update(minbalance=form1.cleaned_data["minbalance"])
                    else:
                        interest, _ = InterestBearing.objects.get_or_create(
                            bankid=bankAcct,
                            accountid=bankAcct.accountid,
                        )
                        InterestBearing.objects.filter(
                            bankid=bankAcct,
                            accountid=bankAcct.accountid,
                        ).update(
                            interest_rate=form1.cleaned_data["interestRate"],
                            dtdeposit=now,
                        )
                        market = Market.objects.get_or_create(
                            bankid=interest,
                            accountid=interest.accountid,
                        )
                        Market.objects.filter(
                            bankid=interest, accountid=interest.accountid
                        ).update(maxwithdrawals=form1.cleaned_data["maxwithdrawals"])
                    messages.success(request, "Account Saved")

            elif "access" in request.POST and form2.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                bankid = form2.cleaned_data["bankID"]
                accountid = form2.cleaned_data["accountID"]
                sharerid = form2.cleaned_data["sharerID"]

                if (
                    len(
                        Access.objects.filter(
                            bankid=bankid, accountid=accountid, perid=sharerid
                        )
                    )
                    > 0
                ):
                    messages.error(request, "Access already exists")
                else:
                    if (
                        len(
                            BankAccount.objects.filter(
                                bankid=bankid, accountid=accountid
                            )
                        )
                        == 0
                    ):
                        messages.error(request, "Access does not exists")
                    else:
                        bankAcct = BankAccount.objects.get(
                            bankid=bankid, accountid=accountid
                        )
                        access, _ = Access.objects.get_or_create(
                            bankid=bankAcct,
                            accountid=bankAcct.accountid,
                            perid=Customer.objects.get(pk=sharerid),
                            dtsharestart=datetime.datetime.now(),
                        )
                        messages.success(request, "Sharer successfully added!")
            else:
                messages.error(request, "Form did not work")

        form1 = AddAccountForm(customers=get_Customers(), banks=get_Banks())
        form2 = AddAccountAccessForm(
            customers=get_Customers(), banks=get_Banks(), accounts=get_Accounts()
        )
        return render(
            request,
            "bank/add_account_access_admin.html",
            {"form1": form1, "form2": form2},
        )
    elif (
        "perID" in request.session
        and request.session["perID"] is not None
        and request.session["isCustomer"]
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form = AddAccountAccessForm(
                request.POST,
                customers=get_Customers(),
                banks=get_Banks(),
                accounts=get_Accounts(),
            )
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                bankid = form.cleaned_data["bankID"]
                accountid = form.cleaned_data["accountID"]
                sharerid = form.cleaned_data["sharerID"]

                if (
                    len(
                        Access.objects.filter(
                            bankid=bankid,
                            accountid=accountid,
                            perid=request.session["perID"],
                        )
                    )
                    == 0
                ):
                    messages.error(
                        request, "Cannot modify an account you don't have access to!"
                    )

                elif (
                    len(
                        Access.objects.filter(
                            bankid=bankid, accountid=accountid, perid=sharerid
                        )
                    )
                    > 0
                ):
                    messages.error(request, "Access already exists")
                else:
                    if (
                        len(
                            BankAccount.objects.filter(
                                bankid=bankid, accountid=accountid
                            )
                        )
                        == 0
                    ):
                        messages.error(request, "Access does not exists")
                    else:
                        bankAcct = BankAccount.objects.get(
                            bankid=bankid, accountid=accountid
                        )
                        access, _ = Access.objects.get_or_create(
                            bankid=bankAcct,
                            accountid=bankAcct.accountid,
                            perid=Customer.objects.get(pk=sharerid),
                            dtsharestart=datetime.datetime.now(),
                        )
                        messages.success(request, "Sharer successfully added!")
        form = AddAccountAccessForm(
            customers=get_Customers(), banks=get_Banks(), accounts=get_Accounts()
        )
        return render(request, "bank/add_account_access_customer.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/")


# Query 10
@never_cache
def remove_account_access(request):
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isAdmin"] or request.session["isCustomer"])
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form = RemoveAccountAccessForm(
                request.POST,
                accounts=get_Accounts(),
                banks=get_Banks(),
                bank_users=get_Bank_users(),
            )
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                if (
                    request.session["perID"] is not None and request.session["isAdmin"]
                ) or (
                    len(
                        Access.objects.filter(
                            bankid=form.cleaned_data["bankID"],
                            accountid=form.cleaned_data["accountID"],
                            perid=request.session["perID"],
                        )
                    )
                    > 0
                ):
                    if (
                        len(
                            Access.objects.filter(
                                bankid=form.cleaned_data["bankID"],
                                accountid=form.cleaned_data["accountID"],
                                perid=form.cleaned_data["sharer"],
                            )
                        )
                        == 0
                    ):
                        messages.error(request, "Sharer already does not have access")
                    else:
                        Access.objects.filter(
                            bankid=form.cleaned_data["bankID"],
                            accountid=form.cleaned_data["accountID"],
                            perid=form.cleaned_data["sharer"],
                        ).delete()
                        if (
                            len(
                                Access.objects.filter(
                                    bankid=form.cleaned_data["bankID"],
                                    accountid=form.cleaned_data["accountID"],
                                )
                            )
                            < 1
                        ):
                            InterestBearingFees.objects.filter(
                                bankid=form.cleaned_data["bankID"],
                                accountid=form.cleaned_data["accountID"],
                            ).delete()
                            Checking.objects.filter(
                                bankid=form.cleaned_data["bankID"],
                                accountid=form.cleaned_data["accountID"],
                            ).delete()
                            Savings.objects.filter(
                                bankid=form.cleaned_data["bankID"],
                                accountid=form.cleaned_data["accountID"],
                            ).delete()
                            InterestBearing.objects.filter(
                                bankid=form.cleaned_data["bankID"],
                                accountid=form.cleaned_data["accountID"],
                            ).delete()
                            BankAccount.objects.filter(
                                bankid=form.cleaned_data["bankID"],
                                accountid=form.cleaned_data["accountID"],
                            ).delete()
                        messages.success(request, "Access Removed Successfully!")
                else:
                    messages.error(request, "Requester does not have authorization!")
        # if a GET (or any other method) we'll create a blank form
        else:
            form = RemoveAccountAccessForm(
                accounts=get_Accounts(), banks=get_Banks(), bank_users=get_Bank_users()
            )
        return render(request, "bank/remove_account_access.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/")


#### Query 11
@never_cache
def create_fee(request):
    if request.method == "POST":
        form = CreateFeeForm(request.POST, meow=get_Banks(), potato=get_Accounts())
        if form.is_valid():

            # 	if exists (select * from interest_bearing where bankID = ip_bankID and accountID = ip_accountID)
            formBankID = form.cleaned_data["bankID"]
            formAccountID = form.cleaned_data["accountID"]

            if (
                len(
                    InterestBearing.objects.filter(
                        bankid=formBankID, accountid=formAccountID
                    )
                )
                >= 1
            ):

                # insert into interest_bearing_fees values (ip_bankID, ip_accountID, ip_fee_type);
                new_interest_fee, created = InterestBearingFees.objects.get_or_create(
                    bankid=InterestBearing.objects.get(
                        bankid=formBankID, accountid=formAccountID
                    ),
                    accountid=form.cleaned_data["accountID"],
                    fee=form.cleaned_data["feeType"],
                )
                if created:
                    messages.success(request, "Created New Fee")
                else:
                    messages.error(request, "Fee already exists")
            else:
                messages.error(request, "Account/Bank Combination does not exist")
        else:
            messages.error(request, "Incorrect Form")
    else:
        form = CreateFeeForm(meow=get_Banks(), potato=get_Accounts())

    return render(request, "bank/create_fee.html", {"form": form})


### Query 12
@never_cache
def start_overdraft(request):
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isAdmin"] or request.session["isCustomer"])
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form = StartOverdraftForm(
                request.POST, accounts=get_Accounts(), banks=get_Banks()
            )
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                if (
                    request.session["perID"] is not None and request.session["isAdmin"]
                ) or (
                    (
                        len(
                            Access.objects.filter(
                                bankid=form.cleaned_data["checkingBankID"],
                                accountid=form.cleaned_data["checkingAccountID"],
                                perid=request.session["perID"],
                            )
                        )
                        > 0
                    )
                    and (
                        len(
                            Access.objects.filter(
                                bankid=form.cleaned_data["savingsBankID"],
                                accountid=form.cleaned_data["savingsAccountID"],
                                perid=request.session["perID"],
                            )
                        )
                        > 0
                    )
                ):
                    Checking.objects.filter(
                        bankid=form.cleaned_data["checkingBankID"],
                        accountid=form.cleaned_data["checkingAccountID"],
                    ).update(
                        protectionbank=form.cleaned_data["savingsBankID"],
                        protectionaccount=form.cleaned_data["savingsAccountID"],
                        amount=None,
                        dtoverdraft=None,
                    )
                    messages.success(request, "Started Overdraft Successfully!")
                else:
                    messages.error(request, "Requester does not have authorization!")
        # if a GET (or any other method) we'll create a blank form
        else:
            form = StartOverdraftForm(accounts=get_Accounts(), banks=get_Banks())

        return render(request, "bank/start_overdraft.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/")


# Query 13
@never_cache
def stop_overdraft(request):
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isAdmin"] or request.session["isCustomer"])
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form = StopOverdraftForm(
                request.POST, accounts=get_Accounts(), banks=get_Banks()
            )
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                if (
                    request.session["perID"] is not None and request.session["isAdmin"]
                ) or (
                    len(
                        Access.objects.filter(
                            bankid=form.cleaned_data["checkingBankID"],
                            accountid=form.cleaned_data["checkingAccountID"],
                            perid=request.session["perID"],
                        )
                    )
                    > 0
                ):
                    Checking.objects.filter(
                        bankid=form.cleaned_data["checkingBankID"],
                        accountid=form.cleaned_data["checkingAccountID"],
                    ).update(
                        protectionbank=None,
                        protectionaccount=None,
                    )
                    messages.success(request, "Stopped Overdraft Successfully!")
                else:
                    messages.error(request, "Requester does not have authorization!")
        # if a GET (or any other method) we'll create a blank form
        else:
            form = StopOverdraftForm(accounts=get_Accounts(), banks=get_Banks())

        return render(request, "bank/stop_overdraft.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/")


### Query 14
def account_deposit(request):
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isCustomer"])
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form = AccountDepositForm(
                request.POST, accounts=get_Accounts(), banks=get_Banks()
            )
            today = datetime.datetime.now()
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                if (
                    len(
                        Access.objects.filter(
                            bankid=form.cleaned_data["bankID"],
                            accountid=form.cleaned_data["accountID"],
                            perid=request.session["perID"],
                        )
                    )
                    > 0
                ):
                    bal = int(
                        BankAccount.objects.filter(
                            bankid=form.cleaned_data["bankID"],
                            accountid=form.cleaned_data["accountID"],
                        ).values_list("balance", flat=True)[0]
                    )
                    if bal == None:
                        bal = 0
                    BankAccount.objects.filter(
                        bankid=form.cleaned_data["bankID"],
                        accountid=form.cleaned_data["accountID"],
                    ).update(balance=bal + form.cleaned_data["depositAmount"])
                    Access.objects.filter(
                        perid=request.session["perID"],
                        bankid=form.cleaned_data["bankID"],
                        accountid=form.cleaned_data["accountID"],
                    ).update(dtaction=today)
                    messages.success(request, "Deposited to Account Successfully!")
                else:
                    messages.error(request, "Requester does not have authorization!")
        # if a GET (or any other method) we'll create a blank form
        else:
            form = AccountDepositForm(accounts=get_Accounts(), banks=get_Banks())

        return render(request, "bank/account_deposit.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/")


### Query 15
@never_cache
def account_withdrawal(request):
    cache.clear()
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isCustomer"])
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form = AccountWithdrawalForm(
                request.POST, banks=get_Banks(), accounts=get_Accounts()
            )
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                bankID = form.cleaned_data["bankID"]
                accountID = form.cleaned_data["accountID"]
                amount = form.cleaned_data["amount"]

                perID = request.session["perID"]

                if (
                    len(
                        Access.objects.filter(
                            bankid=bankID, accountid=accountID, perid=perID
                        )
                    )
                    == 0
                ):
                    messages.error(request, "Person does not have access")

                elif is_checking(bankID, accountID):
                    balance = (
                        BankAccount.objects.get(
                            bankid=bankID, accountid=accountID
                        ).balance
                        or 0
                    )
                    protectionBank = Checking.objects.get(
                        bankid=bankID, accountid=accountID
                    ).protectionbank
                    protectionAccount = Checking.objects.get(
                        bankid=bankID, accountid=accountID
                    ).protectionaccount
                    if (
                        len(
                            BankAccount.objects.filter(
                                bankid=protectionBank, accountid=protectionAccount
                            )
                        )
                        == 0
                    ):
                        overdraft_balance = 0
                    else:
                        overdraft_balance = (
                            BankAccount.objects.get(
                                bankid=protectionBank, accountid=protectionAccount
                            ).balance
                            or 0
                        )
                    if amount > (balance + overdraft_balance):
                        messages.error(
                            request,
                            "Withdrawal amount cant be greater than balance checking amount plus overdraft balance",
                        )
                    elif amount > balance:
                        BankAccount.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(balance=0)
                        BankAccount.objects.filter(
                            bankid=protectionBank, accountid=protectionAccount
                        ).update(balance=overdraft_balance - (amount - balance))
                        current_date_time = datetime.datetime.now()
                        Access.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(dtaction=current_date_time)
                        Access.objects.filter(
                            bankid=protectionBank, accountid=protectionAccount
                        ).update(dtaction=current_date_time)
                        Checking.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(dtoverdraft=current_date_time)
                        Checking.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(amount=amount - balance)
                        messages.success(
                            request, "Withdrew Amount from Checking + Overdraft"
                        )
                    else:
                        BankAccount.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(balance=balance - amount)
                        current_date_time = datetime.datetime.now()
                        Access.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(dtaction=current_date_time)
                        messages.success(request, "Withdrew Amount")
                else:
                    balance = (
                        BankAccount.objects.get(
                            bankid=bankID, accountid=accountID
                        ).balance
                        or 0
                    )
                    if amount > balance:
                        messages.error(
                            request,
                            "Withdrawal amount cant be greater than balance saving/market account",
                        )
                    else:

                        if (
                            len(
                                Market.objects.filter(
                                    bankid=bankID, accountid=accountID
                                )
                            )
                            > 0
                        ):
                            numwithdrawals = Market.objects.get(
                                bankid=bankID, accountid=accountID
                            ).numwithdrawals
                            if (
                                Market.objects.get(
                                    bankid=bankID, accountid=accountID
                                ).maxwithdrawals
                                == numwithdrawals
                            ):
                                messages.error(request, "Max Withdrawals Reached")
                            else:
                                Market.objects.filter(
                                    bankid=bankID, accountid=accountID
                                ).update(numwithdrawals=numwithdrawals + 1)
                                BankAccount.objects.filter(
                                    bankid=bankID, accountid=accountID
                                ).update(balance=balance - (amount))
                                current_date_time = datetime.datetime.now()
                                Access.objects.filter(
                                    bankid=bankID, accountid=accountID
                                ).update(dtaction=current_date_time)
                        else:
                            BankAccount.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(balance=balance - (amount))
                            current_date_time = datetime.datetime.now()
                            Access.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(dtaction=current_date_time)
            else:
                messages.error(request, "Invalid Form")

        # if a GET (or any other method) we'll create a blank form
        else:
            form = AccountWithdrawalForm(banks=get_Banks(), accounts=get_Accounts())

        return render(request, "bank/account_withdrawal.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/index")


### Query 16
@never_cache
def account_transfer(request):
    today = datetime.datetime.now()
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isCustomer"])
    ):
        if request.method == "POST":
            # create a form instance and populate it with data from the request:
            form = AccountTransferForm(
                request.POST, accounts=get_Accounts(), banks=get_Banks()
            )
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                if (
                    len(
                        Access.objects.filter(
                            bankid=form.cleaned_data["fromBankID"],
                            accountid=form.cleaned_data["fromAccountID"],
                            perid=request.session["perID"],
                        )
                    )
                    > 0
                ) and (
                    len(
                        Access.objects.filter(
                            bankid=form.cleaned_data["toBankID"],
                            accountid=form.cleaned_data["toAccountID"],
                            perid=request.session["perID"],
                        )
                    )
                    > 0
                ):
                    ogbal = int(
                        BankAccount.objects.filter(
                            bankid=form.cleaned_data["fromBankID"],
                            accountid=form.cleaned_data["fromAccountID"],
                        ).values_list("balance", flat=True)[0]
                    )
                    if ogbal == None:
                        ogbal = 0

                    # withdrawal from account
                    if is_checking(
                        form.cleaned_data["fromBankID"],
                        form.cleaned_data["fromAccountID"],
                    ):
                        balance = (
                            BankAccount.objects.get(
                                bankid=form.cleaned_data["fromBankID"],
                                accountid=form.cleaned_data["fromAccountID"],
                            ).balance
                            or 0
                        )
                        bankID = form.cleaned_data["fromBankID"]
                        accountID = form.cleaned_data["fromAccountID"]
                        protection_bank_id = Checking.objects.get(
                            bankid=form.cleaned_data["fromBankID"],
                            accountid=form.cleaned_data["fromAccountID"],
                        ).protectionbank
                        protection_account_id = Checking.objects.get(
                            bankid=form.cleaned_data["fromBankID"],
                            accountid=form.cleaned_data["fromAccountID"],
                        ).protectionaccount
                        if protection_bank_id and protection_account_id:
                            saving_account_balance = BankAccount.objects.filter(
                                bankid=protection_bank_id,
                                accountid=protection_account_id,
                            ).balance
                        else:
                            saving_account_balance = 0
                        if form.cleaned_data["transferAmount"] > (
                            balance + saving_account_balance
                        ):
                            messages.error(
                                request,
                                "Withdrawal amount cant be greater than balance checking amount plus overdraft balance",
                            )
                        elif form.cleaned_data["transferAmount"] <= balance:
                            BankAccount.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(
                                balance=balance - form.cleaned_data["transferAmount"]
                            )
                            Access.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(dtaction=today)
                            print(bankID)
                            print(accountID)
                            messages.success(request, "Withdrew Amount")
                        else:
                            bankID = (form.cleaned_data["fromBankID"],)
                            accountID = (form.cleaned_data["fromAccountID"],)
                            BankAccount.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(balance=0)
                            BankAccount.objects.filter(
                                bankid=protection_bank_id,
                                accountid=protection_account_id,
                            ).update(
                                balance=saving_account_balance
                                - (form.cleaned_data["transferAmount"] - balance)
                            )
                            Access.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(dtaction=today)
                            Access.objects.filter(
                                bankid=protection_bank_id,
                                accountid=protection_account_id,
                            ).update(dtaction=today)
                            Checking.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(dtoverdraft=today)
                            Checking.objects.filter(
                                bankid=bankID, accountid=accountID
                            ).update(
                                amount=(form.cleaned_data["transferAmount"] - balance)
                            )
                            messages.success(
                                request, "Withdrew Amount from Checking + Overdraft"
                            )

                    else:
                        balance = (
                            BankAccount.objects.get(
                                bankid=bankID, accountid=accountID
                            ).balance
                            or 0
                        )
                        if form.cleaned_data["transferAmount"] > balance:
                            messages.error(
                                request,
                                "Withdrawal amount cant be greater than balance saving/market account",
                            )
                        else:
                            if (
                                len(
                                    Market.objects.filter(
                                        bankid=bankID, accountid=accountID
                                    )
                                )
                                > 0
                            ):
                                numwithdrawals = Market.objects.get(
                                    bankid=bankID, accountid=accountID
                                ).numwithdrawals
                                if (
                                    Market.objects.get(
                                        bankid=bankID, accountid=accountID
                                    ).maxwithdrawals
                                    == numwithdrawals
                                ):
                                    messages.error(request, "Max Withdrawals Reached")
                                else:
                                    Market.objects.filter(
                                        bankid=bankID, accountid=accountID
                                    ).update(numwithdrawals=numwithdrawals + 1)
                                    BankAccount.objects.filter(
                                        bankid=bankID, accountid=accountID
                                    ).update(
                                        balance=balance
                                        - (form.cleaned_data["transferAmount"])
                                    )
                                    Access.objects.filter(
                                        bankid=bankID, accountid=accountID
                                    ).update(dtaction=today)
                            else:
                                BankAccount.objects.filter(
                                    bankid=bankID, accountid=accountID
                                ).update(
                                    balance=balance
                                    - (form.cleaned_data["transferAmount"])
                                )
                                Access.objects.filter(
                                    bankid=bankID, accountid=accountID
                                ).update(dtaction=today)

                    if ogbal != int(
                        BankAccount.objects.filter(
                            bankid=form.cleaned_data["fromBankID"],
                            accountid=form.cleaned_data["fromAccountID"],
                        ).values_list("balance", flat=True)[0]
                    ):
                        # deposit to account
                        bal = int(
                            BankAccount.objects.filter(
                                bankid=form.cleaned_data["toBankID"],
                                accountid=form.cleaned_data["toAccountID"],
                            ).values_list("balance", flat=True)[0]
                        )
                        if bal == None:
                            bal = 0
                        BankAccount.objects.filter(
                            bankid=form.cleaned_data["toBankID"],
                            accountid=form.cleaned_data["toAccountID"],
                        ).update(balance=bal + form.cleaned_data["transferAmount"])
                        Access.objects.filter(
                            perid=request.session["perID"],
                            bankid=form.cleaned_data["toBankID"],
                            accountid=form.cleaned_data["toAccountID"],
                        ).update(dtaction=today)
                        messages.success(request, "Transferred Successfully!")
                    else:
                        messages.error(request, "Withdrawal failed!")
                else:
                    messages.error(request, "Requester does not have authorization!")

        # if a GET (or any other method) we'll create a blank form
        else:
            form = AccountTransferForm(accounts=get_Accounts(), banks=get_Banks())

        return render(request, "bank/account_transfer.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/")


### Query 17
@never_cache
def pay_employees(request):
    if (
        "perID" in request.session
        and request.session["perID"] is not None
        and (request.session["isAdmin"] or request.session["isManager"])
    ):
        if request.method == "POST":
            employees = get_Employees()
            employee_salary_divison = {}
            bank_deducted_amount = {}
            for employee, _ in employees:
                emp = Employee.objects.get(pk=employee)
                emp.payments = (emp.payments or 0) + 1
                emp.earned = (emp.salary or 0) + (emp.earned or 0)
                emp.save()
                if len(Workfor.objects.filter(perid=employee)) == 0:
                    employee_salary_divison[employee] = 0
                else:
                    employee_salary_divison[employee] = math.floor(
                        (emp.salary or 0) / len(Workfor.objects.filter(perid=employee))
                    )

            for employee in employee_salary_divison.keys():
                salary = employee_salary_divison[employee]
                for bankid in Access.objects.filter(perid=employee).values_list(
                    "bankid", flat=True
                ):
                    bank = Bank.objects.get(pk=bankid)
                    bank.resassets = (bank.resassets or 0) - salary
                    bank.save()
            messages.success(request, "Employees Paid!")
        return render(request, "bank/pay_employees.html")

    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/")


### Query 20
# need to display name_of_bank, account_identifier, account_assets, number_of_owners
def display_account_stats(request):
    if request.session["perID"] is not None and request.session["isAdmin"]:
        all_account_data = BankAccount.objects.all()
        all_access_data = Access.objects.all()
        all_bank_data = Bank.objects.all()

        joined_table = []

        for account_id, bank_id, balance in all_account_data.values_list(
            "accountid", "bankid", "balance"
        ):
            new_entry = {}

            num_access = (
                all_access_data.filter(accountid=account_id)
                .filter(bankid=bank_id)
                .count()
            )
            bank_name = (
                all_bank_data.filter(bankid=bank_id)
                .values_list("bankname", flat=True)
                .get()
            )

            new_entry["bank_name"] = bank_name
            new_entry["account_id"] = account_id
            new_entry["balance"] = balance
            new_entry["num_owners"] = num_access

            joined_table.append(new_entry)

        context = {"joined_table": joined_table}
        return render(request, "bank/display_account_stats.html", context)
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/index")


# sums all balances of accounts in accounts_data
def bank_assets_helper(bank_id, res_assets):
    all_account_data = BankAccount.objects.all()

    accounts_data = all_account_data.filter(bankid=bank_id)
    total_account_balance = accounts_data.filter(balance__isnull=False).aggregate(
        total_balance=Sum("balance")
    )["total_balance"]

    total_assets = int(total_account_balance or 0) + int(res_assets or 0)

    return total_assets


### Query 21
# need bank_identifier, name_of_corporation, name_of_bank, street, city, state, zip, number_of_accounts, bank_assets, total_assets
def display_bank_stats(request):
    if request.session["perID"] is not None and request.session["isAdmin"]:
        all_bank_data = Bank.objects.all()
        all_account_data = BankAccount.objects.all()
        all_corp_data = Corporation.objects.all()

        joined_table = []

        for (
            bank_id,
            bank_name,
            corp_id,
            street,
            city,
            state,
            zip_code,
            res_assets,
        ) in all_bank_data.values_list(
            "bankid",
            "bankname",
            "corpid",
            "street",
            "city",
            "state",
            "zip",
            "resassets",
        ):
            new_entry = {}

            corp_name = (
                all_corp_data.filter(corpid=corp_id)
                .values_list("shortname", flat=True)
                .get()
            )

            total_assets = bank_assets_helper(bank_id, res_assets)

            accounts_data = all_account_data.filter(bankid=bank_id)

            new_entry["bank_id"] = bank_id
            new_entry["corp_name"] = corp_name
            new_entry["bank_name"] = bank_name
            new_entry["street"] = street
            new_entry["city"] = city
            new_entry["state"] = state
            new_entry["zip"] = zip_code
            new_entry["num_accounts"] = accounts_data.count()
            new_entry["bank_assets"] = int(res_assets or 0)
            new_entry["total_assets"] = total_assets

            joined_table.append(new_entry)

        context = {"joined_table": joined_table}
        return render(request, "bank/display_bank_stats.html", context)
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/index")


### Query 22
# need corporation_identifier, short_name, formal_name, number_of_banks, corporation_assets, total_assets
def display_corporation_stats(request):
    if request.session["perID"] is not None and request.session["isAdmin"]:
        all_corp_data = Corporation.objects.all()
        all_bank_data = Bank.objects.all()

        joined_table = []

        for corp_id, short_name, formal_name, res_assets in all_corp_data.values_list(
            "corpid", "shortname", "longname", "resassets"
        ):
            new_entry = {}

            # bank_data is a set query of all banks matching corp_id
            bank_data = all_bank_data.filter(corpid=corp_id)

            total_corp_assets = int(res_assets or 0)
            for bank_id in bank_data.values_list("bankid", flat=True):
                bank_res_assets = (
                    bank_data.filter(bankid=bank_id)
                    .values_list("resassets", flat=True)
                    .get()
                )
                total_corp_assets += bank_assets_helper(bank_id, bank_res_assets)

            new_entry["corp_id"] = corp_id
            new_entry["short_name"] = short_name
            new_entry["formal_name"] = formal_name
            new_entry["num_banks"] = bank_data.count()
            new_entry["corp_assets"] = int(res_assets or 0)
            new_entry["total_assets"] = total_corp_assets

            joined_table.append(new_entry)

        context = {"joined_table": joined_table}
        return render(request, "bank/display_corporation_stats.html", context)
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/index")


### Query 23
# need person_identifier, tax_identifier, customer_name, date_of_birth, joined_system, street, city, state, zip, number_of_accounts, customer_assets
def display_customer_stats(request):
    if request.session["perID"] is not None and request.session["isAdmin"]:
        all_customer_data = Customer.objects.all()
        all_bank_user_data = BankUser.objects.all()
        all_access_data = Access.objects.all()
        all_account_data = BankAccount.objects.all()

        joined_table = []

        for per_id in all_customer_data.values_list("perid", flat=True):
            new_entry = {}

            bank_user_data = all_bank_user_data.filter(perid=per_id)
            (
                tax_identifier,
                first_name,
                last_name,
                date_of_birth,
                joined_system,
                street,
                city,
                state,
                zip_code,
            ) = bank_user_data.values_list(
                "taxid",
                "firstname",
                "lastname",
                "dtjoined",
                "dtjoined",
                "street",
                "city",
                "state",
                "zip",
            ).get()

            # query set of all access relationships with this customer
            access_data = all_access_data.filter(perid=per_id)

            customer_assets = 0

            # loop through all customer-account relationships
            for account_id, bank_id in access_data.values_list("accountid", "bankid"):
                # get account
                account_data = all_account_data.filter(accountid=account_id).filter(
                    bankid=bank_id
                )
                customer_assets += int(
                    account_data.values_list("balance", flat=True).get() or 0
                )

            new_entry["per_id"] = per_id
            new_entry["tax_id"] = tax_identifier
            new_entry["customer_name"] = first_name + " " + last_name
            new_entry["date_of_birth"] = date_of_birth
            new_entry["joined_system"] = joined_system
            new_entry["street"] = street
            new_entry["city"] = city
            new_entry["state"] = state
            new_entry["zip"] = zip_code
            new_entry["number_of_accounts"] = access_data.count()
            new_entry["customer_assets"] = customer_assets

            joined_table.append(new_entry)

        context = {"joined_table": joined_table}
        return render(request, "bank/display_customer_stats.html", context)
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/index")


### Query 24
# need person_identifier, tax_identifier, employee_name, date_of_birth, joined_system, street, city, state, zip, number_of_banks, bank_assets
def display_employee_stats(request):
    if request.session["perID"] is not None and request.session["isAdmin"]:
        all_employee_data = Employee.objects.all()
        all_bank_user_data = BankUser.objects.all()
        all_work_for_data = Workfor.objects.all()
        all_bank_data = Bank.objects.all()
        all_account_data = BankAccount.objects.all()

        joined_table = []

        for per_id in all_employee_data.values_list("perid", flat=True):
            new_entry = {}

            bank_user_data = all_bank_user_data.filter(perid=per_id)
            (
                tax_identifier,
                first_name,
                last_name,
                date_of_birth,
                joined_system,
                street,
                city,
                state,
                zip_code,
            ) = bank_user_data.values_list(
                "taxid",
                "firstname",
                "lastname",
                "dtjoined",
                "dtjoined",
                "street",
                "city",
                "state",
                "zip",
            ).get()

            # query set of all workFor relationships with this employee
            work_for_data = all_work_for_data.filter(perid=per_id)

            employee_assets = 0

            # loop through all employee-bank relationships
            for bank_id in work_for_data.values_list("bankid", flat=True):
                bank_res_assets = (
                    all_bank_data.filter(bankid=bank_id)
                    .values_list("resassets", flat=True)
                    .get()
                )
                employee_assets += bank_assets_helper(bank_id, bank_res_assets)

            new_entry["per_id"] = per_id
            new_entry["tax_id"] = tax_identifier
            new_entry["employee_name"] = str(first_name) + " " + str(last_name)
            new_entry["date_of_birth"] = date_of_birth
            new_entry["joined_system"] = joined_system
            new_entry["street"] = street
            new_entry["city"] = city
            new_entry["state"] = state
            new_entry["zip"] = zip_code
            new_entry["number_of_banks"] = work_for_data.count()
            new_entry["bank_assets"] = employee_assets

            joined_table.append(new_entry)

        context = {"joined_table": joined_table}
        return render(request, "bank/display_employee_stats.html", context)
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/index")
