from django import forms
from .models import Employee, Person, Corporation


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


class CreateCorporationForm(forms.Form):
    corpID = forms.CharField(label="Corporation ID", max_length=100)
    shortName = forms.CharField(label="Short Name", max_length=100)
    longName = forms.CharField(label="Long Name", max_length=100)
    resAssets = forms.IntegerField(label="Reserved Assets", required=False)


class CreateBankForm(forms.Form):
    bankID = forms.CharField(label="Bank ID", max_length=100)
    bankName = forms.CharField(label="Bank Name", max_length=100)
    street = forms.CharField(label="Street", max_length=100)
    city = forms.CharField(label="City", max_length=100)
    state = forms.CharField(label="State", max_length=100)
    zip_code = forms.CharField(label="Zip", max_length=100)
    resAssets = forms.IntegerField(label="Reserved Assets", required=False)
    corpID = forms.CharField(
        label="Corporation", widget=forms.Select(choices=get_Corporations())
    )
    manager = forms.CharField(
        label="Manager", widget=forms.Select(choices=get_Employees())
    )
    bank_employee = forms.CharField(
        label="Employee", widget=forms.Select(choices=get_Employees())
    )


class RemoveAccountAccessForm(forms.Form):
    requester = forms.CharField(label="Requester", max_length=100)
    sharer = forms.CharField(label="Sharer", max_length=100)
    bankID = forms.CharField(label="Bank ID", max_length=100)
    accountID = forms.CharField(label="Account ID", max_length=100)


class StartOverdraftForm(forms.Form):
    requester = forms.CharField(label="Requester", max_length=100)
    checkingBankID = forms.CharField(label="Checking Bank ID", max_length=100)
    checkingAccountID = forms.CharField(label="Checking Account ID", max_length=100)
    savingsBankID = forms.CharField(label="Savings Bank ID", max_length=100)
    savingsAccountID = forms.CharField(label="Savings Account ID", max_length=100)


class StopOverdraftForm(forms.Form):
    requester = forms.CharField(label="Requester", max_length=100)
    checkingBankID = forms.CharField(label="Checking Bank ID", max_length=100)
    checkingAccountID = forms.CharField(label="Checking Account ID", max_length=100)


class AccountDepositForm(forms.Form):
    requester = forms.CharField(label="Requester", max_length=100)
    depositAmount = forms.IntegerField(label="Deposit Amount")
    bankID = forms.CharField(label="Bank ID", max_length=100)
    accountID = forms.CharField(label="Account ID", max_length=100)
    dtAction = forms.DateField(label="Date of Action")


class AccountTransferForm(forms.Form):
    requester = forms.CharField(label="Requester", max_length=100)
    transferAmount = forms.IntegerField(label="Transfer Amount")
    fromBankID = forms.CharField(label="Bank ID", max_length=100)
    fromAccountID = forms.CharField(label="Account ID", max_length=100)
    fromBankID = forms.CharField(label="Bank ID", max_length=100)
    fromAccountID = forms.CharField(label="Account ID", max_length=100)
    dtAction = forms.DateField(label="Date of Action")
