from django import forms
from .models import Employee, Person, Corporation, Bank, BankAccount
from django.views.decorators.cache import never_cache
from django.core.cache import cache


class LoginForm(forms.Form):
    perID = forms.CharField(label="User ID", max_length=100)
    pwd = forms.CharField(label="Password", max_length=100)


class CreateCorporationForm(forms.Form):
    corpID = forms.CharField(label="Corporation ID", max_length=100)
    shortName = forms.CharField(label="Short Name", max_length=100)
    longName = forms.CharField(label="Long Name", max_length=100)
    resAssets = forms.IntegerField(label="Reserved Assets", required=False)


class CreateBankForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.corporations = kwargs.pop("corporations", None)
        self.employees = kwargs.pop("employees")
        super(CreateBankForm, self).__init__(*args, **kwargs)
        self.fields["manager"].widget = forms.Select(choices=self.employees)
        self.fields["bank_employee"].widget = forms.Select(choices=self.employees)
        self.fields["corpID"].widget = forms.Select(choices=self.corporations)

    bankID = forms.CharField(label="Bank ID", max_length=100)
    bankName = forms.CharField(label="Bank Name", max_length=100)
    street = forms.CharField(label="Street", max_length=100)
    city = forms.CharField(label="City", max_length=100)
    state = forms.CharField(label="State", max_length=100)
    zip_code = forms.CharField(label="Zip", max_length=100)
    resAssets = forms.IntegerField(label="Reserved Assets", required=False)
    corpID = forms.CharField(label="Corporation")
    manager = forms.CharField(label="Manager")
    bank_employee = forms.CharField(label="Employee")

    class Meta:
        model = Bank
        fields = (
            "bankid",
            "bankname",
            "street",
            "city",
            "state",
            "zip",
            "resassets",
            "corpid",
            "manager",
            "bank_employee",
        )


class HireEmployeeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.employees = kwargs.pop("employees")
        self.banks = kwargs.pop("banks")
        super(HireEmployeeForm, self).__init__(*args, **kwargs)
        self.fields["bankID"].widget = forms.Select(choices=self.banks)
        self.fields["perID"].widget = forms.Select(choices=self.employees)

    bankID = forms.CharField(label="Bank ID")
    perID = forms.CharField(label="Employee")
    salary = forms.IntegerField(label="Salary")

    class Meta:
        model = Employee
        fields = (
            "bankid",
            "perid",
            "salary",
        )


class ReplaceManagerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.employees = kwargs.pop("employees")
        self.banks = kwargs.pop("banks")
        super(ReplaceManagerForm, self).__init__(*args, **kwargs)
        self.fields["bankID"].widget = forms.Select(choices=self.banks)
        self.fields["perID"].widget = forms.Select(choices=self.employees)

    bankID = forms.CharField(label="Bank ID")
    perID = forms.CharField(label="Employee")
    salary = forms.IntegerField(label="Salary")

    class Meta:
        model = Employee
        fields = (
            "bankid",
            "perid",
            "salary",
        )


class AccountWithdrawalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.accounts = kwargs.pop("accounts")
        self.banks = kwargs.pop("banks")
        super(AccountWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields["bankID"].widget = forms.Select(choices=self.banks)
        self.fields["accountID"].widget = forms.Select(choices=self.accounts)

    bankID = forms.CharField(label="Bank ID")
    accountID = forms.CharField(label="Account ID")
    amount = forms.IntegerField(label="amount")

    class Meta:
        model = BankAccount
        fields = (
            "bankid",
            "accountID",
            "amount",
        )


class RemoveAccountAccessForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.accounts = kwargs.pop("accounts")
        self.banks = kwargs.pop("banks")
        self.bank_users = kwargs.pop("bank_users")
        super(AccountWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields["bankID"].widget = forms.Select(choices=self.banks)
        self.fields["accountID"].widget = forms.Select(choices=self.accounts)
        self.fields["sharer"].widget = forms.Select(choices=self.bank_users)

    sharer = forms.CharField(label="Sharer")
    bankID = forms.CharField(label="Bank ID")
    accountID = forms.CharField(label="Account ID")

    class Meta:
        model = BankAccount
        fields = (
            "sharer",
            "bankID",
            "accountID",
        )


class StartOverdraftForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.accounts = kwargs.pop("accounts")
        self.banks = kwargs.pop("banks")
        super(AccountWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields["checkingBankID"].widget = forms.Select(choices=self.banks)
        self.fields["checkingAccountID"].widget = forms.Select(choices=self.accounts)
        self.fields["savingsBankID"].widget = forms.Select(choices=self.banks)
        self.fields["savingsAccountID"].widget = forms.Select(choices=self.accounts)

    checkingBankID = forms.CharField(label="Checking Bank ID")
    checkingAccountID = forms.CharField(label="Checking Account ID")
    savingsBankID = forms.CharField(label="Savings Bank ID")
    savingsAccountID = forms.CharField(label="Savings Account ID")

    class Meta:
        model = BankAccount
        fields = (
            "checkingBankID",
            "checkingAccountID",
            "savingsBankID",
            "savingsAccountID",
        )


class StopOverdraftForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.accounts = kwargs.pop("accounts")
        self.banks = kwargs.pop("banks")
        super(AccountWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields["checkingBankID"].widget = forms.Select(choices=self.banks)
        self.fields["checkingAccountID"].widget = forms.Select(choices=self.accounts)

    checkingBankID = forms.CharField(label="Checking Bank ID", max_length=100)
    checkingAccountID = forms.CharField(label="Checking Account ID", max_length=100)

    class Meta:
        model = BankAccount
        fields = (
            "checkingBankID",
            "checkingAccountID",
        )


class AccountDepositForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.accounts = kwargs.pop("accounts")
        self.banks = kwargs.pop("banks")
        super(AccountWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields["bankID"].widget = forms.Select(choices=self.banks)
        self.fields["accountID"].widget = forms.Select(choices=self.accounts)

    depositAmount = forms.IntegerField(label="Deposit Amount")
    bankID = forms.CharField(label="Bank ID", max_length=100)
    accountID = forms.CharField(label="Account ID", max_length=100)

    class Meta:
        model = BankAccount
        fields = (
            "depositAmount",
            "bankID",
            "accountID",
        )


class AccountTransferForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.accounts = kwargs.pop("accounts")
        self.banks = kwargs.pop("banks")
        super(AccountWithdrawalForm, self).__init__(*args, **kwargs)
        self.fields["fromBankID"].widget = forms.Select(choices=self.banks)
        self.fields["fromAccountID"].widget = forms.Select(choices=self.accounts)
        self.fields["toBankID"].widget = forms.Select(choices=self.banks)
        self.fields["toAccountID"].widget = forms.Select(choices=self.accounts)

    transferAmount = forms.IntegerField(label="Transfer Amount")
    fromBankID = forms.CharField(label="Bank ID", max_length=100)
    fromAccountID = forms.CharField(label="Account ID", max_length=100)
    toBankID = forms.CharField(label="Bank ID", max_length=100)
    toAccountID = forms.CharField(label="Account ID", max_length=100)

    class Meta:
        model = BankAccount
        fields = (
            "transferAmount",
            "fromBankID",
            "fromAccountID",
            "toBankID",
            "toAccountID",
        )
