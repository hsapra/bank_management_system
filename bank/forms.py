from django import forms
from .models import Employee, Person, Corporation, Bank, BankAccount
from django.views.decorators.cache import never_cache
from django.core.cache import cache

class LoginForm(forms.Form):
    perID = forms.CharField(label='User ID', max_length=100)
    pwd = forms.CharField(label='Password', max_length=100)

class CreateCorporationForm(forms.Form):
    corpID = forms.CharField(label='Corporation ID', max_length=100)
    shortName = forms.CharField(label = 'Short Name', max_length=100)
    longName = forms.CharField(label = 'Long Name', max_length=100)
    resAssets = forms.IntegerField(label='Reserved Assets', required=False)

class CreateBankForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.corporations = kwargs.pop('corporations', None)
        self.employees = kwargs.pop('employees')
        super(CreateBankForm, self).__init__(*args, **kwargs)
        self.fields['manager'].widget = forms.Select(choices=self.employees)
        self.fields['bank_employee'].widget = forms.Select(choices=self.employees)
        self.fields['corpID'].widget = forms.Select(choices=self.corporations)

    bankID = forms.CharField(label='Bank ID', max_length=100)
    bankName = forms.CharField(label = 'Bank Name', max_length=100)
    street = forms.CharField(label = 'Street', max_length=100)
    city = forms.CharField(label = 'City', max_length=100)
    state = forms.CharField(label = 'State', max_length=100)
    zip_code = forms.CharField(label = 'Zip', max_length=100)
    resAssets = forms.IntegerField(label='Reserved Assets', required=False)
    corpID = forms.CharField(label='Corporation')
    manager = forms.CharField(label='Manager')
    bank_employee = forms.CharField(label='Employee')

    class Meta:
        model = Bank
        fields = ('bankid', 'bankname', 'street', 'city', 'state', 'zip', 'resassets', 'corpid', 'manager', 'bank_employee',)


class HireEmployeeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.employees = kwargs.pop('employees')
        self.banks = kwargs.pop('banks')
        super(HireEmployeeForm, self).__init__(*args, **kwargs)
        self.fields['bankID'].widget = forms.Select(choices=self.banks)
        self.fields['perID'].widget = forms.Select(choices=self.employees)

    bankID = forms.CharField(label='Bank ID')
    perID = forms.CharField(label='Employee')
    salary = forms.IntegerField(label='Salary')

    class Meta:
        model = Employee
        fields = ('bankid', 'perid', 'salary',)

class ReplaceManagerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.employees = kwargs.pop('employees')
        self.banks = kwargs.pop('banks')
        super(ReplaceManagerForm, self).__init__(*args, **kwargs)
        self.fields['bankID'].widget = forms.Select(choices=self.banks)
        self.fields['perID'].widget = forms.Select(choices=self.employees)

    bankID = forms.CharField(label='Bank ID')
    perID = forms.CharField(label='Employee')
    salary = forms.IntegerField(label='Salary')

    class Meta:
        model = Employee
        fields = ('bankid', 'perid', 'salary',)

class AccountWithdrawalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.accounts = kwargs.pop('accounts')
        self.banks = kwargs.pop('banks')
        super(AccountWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields['bankID'].widget = forms.Select(choices=self.banks)
        self.fields['accountID'].widget = forms.Select(choices=self.accounts)

    bankID = forms.CharField(label='Bank ID')
    accountID = forms.CharField(label='Account ID')
    amount = forms.IntegerField(label='amount')

    class Meta:
        model = BankAccount
        fields = ('bankid', 'accountID', 'amount',)
