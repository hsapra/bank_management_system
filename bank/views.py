from django.shortcuts import render, redirect
import importlib
from django.http import HttpResponse
from django.contrib import messages
import datetime

# Create your views here.
from .forms import (
    CreateCorporationForm,
    CreateBankForm,
    RemoveAccountAccessForm,
    StartOverdraftForm,
    StopOverdraftForm,
    AccountDepositForm,
    AccountTransferForm,
    HireEmployeeForm,
    ReplaceManagerForm,
    LoginForm,
    AccountWithdrawalForm,
)
from bank.models import (
    Corporation,
    Bank,
    Employee,
    SystemAdmin,
    Workfor,
    Access,
    InterestBearing,
    InterestBearingFees,
    Checking,
    Savings,
    BankAccount,
    Customer,
    Person,
    BankUser,
    Market,
)
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.db import IntegrityError
from psycopg2.errorcodes import UNIQUE_VIOLATION

# yyyy-mm-dd
today = datetime.datetime.now().date()


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
        context = {"data": get_url_names()}
        return render(request, "bank/index.html", context)
    else:
        messages.error(
            request, "Access Denied. Please Log In with the correct credentials"
        )
        return redirect("/bank/")


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


@never_cache
def remove_account_access(request):
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


@never_cache
def start_overdraft(request):
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


@never_cache
def stop_overdraft(request):
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
                    amount=None,
                    dtoverdraft=None,
                )
                messages.success(request, "Stopped Overdraft Successfully!")
            else:
                messages.error(request, "Requester does not have authorization!")
    # if a GET (or any other method) we'll create a blank form
    else:
        form = StopOverdraftForm(accounts=get_Accounts(), banks=get_Banks())

    return render(request, "bank/stop_overdraft.html", {"form": form})


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


@never_cache
def account_deposit(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = AccountDepositForm(
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


@never_cache
def account_withdrawal(request):
    cache.clear()
    if request.session["perID"] is not None and request.session["isCustomer"]:
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
                    overdraft_balance = (
                        Checking.objects.get(bankid=bankID, accountid=accountID).amount
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
                        overdraft_bank = Checking.objects.get(
                            bankid=bankID, accountid=accountID
                        ).protectionbank
                        overdraft_account = Checking.objects.get(
                            bankid=bankID, accountid=accountID
                        ).protectionaccount
                        saving_account_balance = BankAccount.objects.filter(
                            bankid=overdraft_bank, accountid=overdraft_account
                        ).balance
                        BankAccount.objects.filter(
                            bankid=overdraft_bank, accountid=overdraft_account
                        ).update(balance=saving_account_balance - (amount - balance))
                        Access.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(dtaction=today)
                        Checking.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(dtoverdraft=today)
                else:
                    BankAccount.objects.filter(
                        bankid=bankID, accountid=accountID
                    ).update(balance=balance - amount)
                    Access.objects.filter(bankid=bankID, accountid=accountID).update(
                        dtaction=today
                    )
            else:
                messages.error(request, "Invalid Form")

        # if a GET (or any other method) we'll create a blank form
        else:
            form = AccountWithdrawalForm(banks=get_Banks(), accounts=get_Accounts())

        return render(request, "bank/account_withdrawal.html", {"form": form})
    else:
        messages.error(request, "Access Denied.")
        return redirect("/bank/index")


@never_cache
def account_transfer(request):
    pass
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
                    form.cleaned_data["fromBankID"], form.cleaned_data["fromAccountID"]
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
                            bankid=protection_bank_id, accountid=protection_account_id
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
                        ).update(balance=balance - form.cleaned_data["transferAmount"])
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
                            bankid=protection_bank_id, accountid=protection_account_id
                        ).update(
                            balance=saving_account_balance
                            - (form.cleaned_data["transferAmount"] - balance)
                        )
                        Access.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(dtaction=today)
                        Checking.objects.filter(
                            bankid=bankID, accountid=accountID
                        ).update(dtoverdraft=today)
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
                                balance=balance - (form.cleaned_data["transferAmount"])
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
