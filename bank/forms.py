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


class RemoveAccountAccess(forms.Form):
    requester = forms.CharField(label="Requester", max_length=100)
    sharer = forms.CharField(label="Sharer", max_length=100)
    bankID = forms.CharField(label="Bank ID", max_length=100)
    accountID = forms.CharField(label="Account ID", max_length=100)
