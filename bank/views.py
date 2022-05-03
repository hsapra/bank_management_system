from django.shortcuts import render, redirect
import importlib
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast

# Create your views here.
from .forms import CreateCorporationForm, CreateBankForm, get_Persons
from bank.models import *
from django.contrib import messages
import datetime


# Create your views here.
from .forms import CreateCorporationForm, CreateBankForm, HireEmployeeForm, ReplaceManagerForm, LoginForm, AccountWithdrawalForm
from bank.models import Corporation, Bank, Employee, Workfor, Person, Customer, SystemAdmin, BankAccount, Checking, Access, Market
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.db import IntegrityError
from psycopg2.errorcodes import UNIQUE_VIOLATION

def get_url_names():
	from django.apps import apps

	list_of_url_names = list()
	list_of_all_urls = list()
	for name, app in apps.app_configs.items():
		mod_to_import = f'{name}.urls'
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
    list_of_accts = list(BankAccount.objects.all().values_list('accountid', flat=True).distinct())

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)] 

    tuple_list = []

    for acct in list_of_accts:
        tuple_list.append((acct, acct))

    return tuple_list

def get_Persons():
    list_of_people = list(Person.objects.all().values_list('perid', flat=True).distinct())

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)] 

    tuple_list = []

    for people in list_of_people:
        tuple_list.append((people, people))

    return tuple_list

def get_Corporations():
    print("Called Corp")
    list_of_corps = list(Corporation.objects.all().values_list('corpid', flat=True).distinct())

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)] 

    tuple_list = []

    for corps in list_of_corps:
        tuple_list.append((corps, corps))

    return tuple_list

def get_Employees():
    list_of_emps = list(Employee.objects.all().values_list('perid', flat=True).distinct())

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)] 

    tuple_list = []

    for emp in list_of_emps:
        tuple_list.append((emp, emp))

    return tuple_list

def get_Banks():
    list_of_banks = list(Bank.objects.all().values_list('bankid', flat=True).distinct())

    # Format needed as (choice, value) and right now the output above is [perId1, perId2......], we need [(perId1, perId1), (perId2, perId2)] 

    tuple_list = []

    for bank in list_of_banks:
        tuple_list.append((bank, bank))

    return tuple_list

def is_checking(bankID, accountID):
	return len(Checking.objects.filter(bankid = bankID, accountid = accountID)) > 0


def login(request):
	if 'perID' in request.session and request.session['perID']:
		return index(request)

	else:
		if request.method == 'POST':
			form = LoginForm(request.POST)
			if form.is_valid():
				perID = form.cleaned_data['perID']
				pwd  = form.cleaned_data['pwd']

				if len(Person.objects.filter(pk=perID)) == 0:
					messages.error(request, "Invalid Username")
				elif Person.objects.get(pk=perID).pwd != pwd:
					messages.error(request, "Invalid Password")
				else:
					messages.success(request, "Logged In")
					request.session['perID'] = perID
					request.session['isCustomer'] = len(Customer.objects.filter(pk=perID)) != 0
					request.session['isAdmin'] = len(SystemAdmin.objects.filter(pk=perID)) != 0
					request.session['isManager'] = len(Bank.objects.filter(manager_id=perID)) != 0
					return index(request)
		else:
			form = LoginForm()
		return render(request, 'bank/login.html', {'form': form})

def logout(request):
	if 'perID' in request.session:
		perID = request.session.pop('perID')
	return redirect('/bank/')

@never_cache
def index(request):
	cache.clear()
	if 'perID' in request.session and request.session['perID']: 
		context = {'data': get_url_names()}
		return render(request, 'bank/index.html', context)
	else:
		messages.error(request, 'Access Denied. Please Log In with the correct credentials')
		return redirect('/bank/')

@never_cache
def create_corporation(request):
	cache.clear()
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateCorporationForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			if len(Corporation.objects.filter(corpid = form.cleaned_data['corpID'])) != 0 or len(Corporation.objects.filter(shortname = form.cleaned_data['shortName'])) != 0 or len(Corporation.objects.filter(longname = form.cleaned_data['longName'])) != 0:
				messages.error(request, 'Data Exists.')
			else:
				new_corp = Corporation(corpid = form.cleaned_data['corpID'], shortname = form.cleaned_data['shortName'], longname = form.cleaned_data['longName'], resassets = form.cleaned_data['resAssets'])
				new_corp.save()
				messages.success(request, 'Corporation Created Successfully!')
		else:
			messages.error(request, 'Invalid form submission.')
			messages.error(request, form.errors)

	# if a GET (or any other method) we'll create a blank form
	else:
		form = CreateCorporationForm()

	context = {'form': form}

	return render(request, 'bank/create_corporation.html', context)

@never_cache
def create_bank(request):
	cache.clear()
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateBankForm(request.POST, corporations=get_Corporations(), employees=get_Employees())
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			if len(Bank.objects.filter(manager_id = form.cleaned_data['manager'])) == 0:
				if len(Bank.objects.filter(manager_id = form.cleaned_data['bank_employee'])) == 0:
					if len(Bank.objects.filter(bankid = form.cleaned_data['bankID'])) == 0:
						new_bank = Bank(
							bankid = form.cleaned_data['bankID'], 
							bankname = form.cleaned_data['bankName'], 
							street = form.cleaned_data['street'], 
							city = form.cleaned_data['city'], 
							state = form.cleaned_data['state'], 
							zip = form.cleaned_data['zip_code'], 
							resassets = form.cleaned_data['resAssets'],
							corpid = Corporation.objects.get(pk = form.cleaned_data['corpID']),
							manager = Employee.objects.get(pk=form.cleaned_data['manager']))
						new_bank.save()
						work_for_employee , created = Workfor.objects.get_or_create(
							bankid = new_bank, 
							perid = Employee.objects.get(pk=form.cleaned_data['bank_employee']))

						if created:
							messages.success(request, 'Bank Created Successfully!')
						else:
							messages.error(request, "Failed to create Employee-Bank Relation")
					else:
						messages.error(request, 'Existing Bank.')
				else:
					messages.error(request, 'Employee cannot be existing manager.')
			else:
				messages.error(request, 'Manager cannot be existing manager.')
				
	# if a GET (or any other method) we'll create a blank form
	else:
		form = CreateBankForm(corporations=get_Corporations(), employees=get_Employees())

	return render(request, 'bank/create_bank.html', {'form': form})

# need to display name_of_bank, account_identifier, account_assets, number_of_owners
def display_account_stats(request):

	all_account_data = BankAccount.objects.all()
	all_access_data = Access.objects.all()
	all_bank_data = Bank.objects.all()

	joined_table = []

	for account_id, bank_id, balance in all_account_data.values_list('accountid', 'bankid', 'balance'):
		new_entry = {}

		num_access = all_access_data.filter(accountid=account_id).filter(bankid=bank_id).count()
		bank_name = all_bank_data.filter(bankid=bank_id).values_list('bankname', flat=True).get()
		
		new_entry['bank_name'] = bank_name
		new_entry['account_id'] = account_id
		new_entry['balance'] = balance
		new_entry['num_owners'] = num_access

		joined_table.append(new_entry)

	context = {'joined_table': joined_table}
	return render(request, 'bank/display_account_stats.html', context)

# sums all balances of accounts in accounts_data
def bank_assets_helper(bank_id, res_assets):
	all_account_data = BankAccount.objects.all()

	accounts_data = all_account_data.filter(bankid=bank_id)
	total_account_balance = accounts_data.filter(balance__isnull=False).aggregate(total_balance=Sum('balance'))['total_balance']

	total_assets = int(total_account_balance or 0) + int(res_assets or 0)

	return total_assets

# need bank_identifier, name_of_corporation, name_of_bank, street, city, state, zip, number_of_accounts, bank_assets, total_assets
def display_bank_stats(request):

	all_bank_data = Bank.objects.all()
	all_account_data = BankAccount.objects.all()
	all_corp_data = Corporation.objects.all()

	joined_table = []

	for bank_id, bank_name, corp_id, street, city, state, zip_code, res_assets in all_bank_data.values_list('bankid', 'bankname', 'corpid', 'street', 'city', 'state', 'zip', 'resassets'):
		new_entry = {}

		corp_name = all_corp_data.filter(corpid=corp_id).values_list('shortname', flat=True).get()
		
		total_assets = bank_assets_helper(bank_id, res_assets)

		accounts_data = all_account_data.filter(bankid=bank_id)

		new_entry['bank_id'] = bank_id
		new_entry['corp_name'] = corp_name
		new_entry['bank_name'] = bank_name
		new_entry['street'] = street
		new_entry['city'] = city
		new_entry['state'] = state
		new_entry['zip'] = zip_code
		new_entry['num_accounts'] = accounts_data.count()
		new_entry['bank_assets'] = int(res_assets or 0)
		new_entry['total_assets'] = total_assets
		
		joined_table.append(new_entry)

	context = {'joined_table': joined_table}
	return render(request, 'bank/display_bank_stats.html', context)

# need corporation_identifier, short_name, formal_name, number_of_banks, corporation_assets, total_assets
def display_corporation_stats(request):

	all_corp_data = Corporation.objects.all()
	all_bank_data = Bank.objects.all()

	joined_table = []

	for corp_id, short_name, formal_name, res_assets in all_corp_data.values_list('corpid', 'shortname', 'longname', 'resassets'):
		new_entry = {}

		# bank_data is a set query of all banks matching corp_id
		bank_data = all_bank_data.filter(corpid=corp_id)

		total_corp_assets = int(res_assets or 0)
		for bank_id in bank_data.values_list('bankid', flat=True):
			bank_res_assets = bank_data.filter(bankid=bank_id).values_list('resassets', flat=True).get()
			total_corp_assets += bank_assets_helper(bank_id, bank_res_assets)

		new_entry['corp_id'] = corp_id
		new_entry['short_name'] = short_name
		new_entry['formal_name'] = formal_name
		new_entry['num_banks'] = bank_data.count()
		new_entry['corp_assets'] = int(res_assets or 0)
		new_entry['total_assets'] = total_corp_assets
		
		joined_table.append(new_entry)

	context = {'joined_table': joined_table}
	return render(request, 'bank/display_corporation_stats.html', context)

# need person_identifier, tax_identifier, customer_name, date_of_birth, joined_system, street, city, state, zip, number_of_accounts, customer_assets
def display_customer_stats(request):

	all_customer_data = Customer.objects.all()
	all_bank_user_data = BankUser.objects.all()
	all_access_data = Access.objects.all()
	all_account_data = BankAccount.objects.all()

	joined_table = []

	for per_id in all_customer_data.values_list('perid', flat=True):
		new_entry = {}

		bank_user_data = all_bank_user_data.filter(perid=per_id)
		tax_identifier, first_name, last_name, date_of_birth, joined_system, street, city, state, zip_code = bank_user_data.values_list('taxid', 'firstname', 'lastname', 'dtjoined', 'dtjoined', 'street', 'city', 'state', 'zip').get()

		# query set of all access relationships with this customer
		access_data = all_access_data.filter(perid=per_id)

		customer_assets = 0

		# loop through all customer-account relationships
		for account_id, bank_id in access_data.values_list('accountid', 'bankid'):
			# get account
			account_data = all_account_data.filter(accountid=account_id).filter(bankid=bank_id)
			customer_assets += int(account_data.values_list('balance', flat=True).get() or 0)

		new_entry['per_id'] = per_id
		new_entry['tax_id'] = tax_identifier
		new_entry['customer_name'] = first_name + ' ' + last_name
		new_entry['date_of_birth'] = date_of_birth
		new_entry['joined_system'] = joined_system
		new_entry['street'] = street
		new_entry['city'] = city
		new_entry['state'] = state
		new_entry['zip'] = zip_code
		new_entry['number_of_accounts'] = access_data.count()
		new_entry['customer_assets'] = customer_assets
		
		joined_table.append(new_entry)

	context = {'joined_table': joined_table}
	return render(request, 'bank/display_customer_stats.html', context)

# need person_identifier, tax_identifier, employee_name, date_of_birth, joined_system, street, city, state, zip, number_of_banks, bank_assets
def display_employee_stats(request):

	all_employee_data = Employee.objects.all()
	all_bank_user_data = BankUser.objects.all()
	all_work_for_data = Workfor.objects.all()
	all_bank_data = Bank.objects.all()
	all_account_data = BankAccount.objects.all()

	joined_table = []

	for per_id in all_employee_data.values_list('perid', flat=True):
		new_entry = {}

		bank_user_data = all_bank_user_data.filter(perid=per_id)
		tax_identifier, first_name, last_name, date_of_birth, joined_system, street, city, state, zip_code = bank_user_data.values_list('taxid', 'firstname', 'lastname', 'dtjoined', 'dtjoined', 'street', 'city', 'state', 'zip').get()

		# query set of all workFor relationships with this employee
		work_for_data = all_work_for_data.filter(perid=per_id)

		employee_assets = 0

		# loop through all employee-bank relationships
		for bank_id in work_for_data.values_list('bankid', flat=True):
			bank_res_assets = all_bank_data.filter(bankid=bank_id).values_list('resassets', flat=True).get()
			employee_assets += bank_assets_helper(bank_id, bank_res_assets)

		new_entry['per_id'] = per_id
		new_entry['tax_id'] = tax_identifier
		new_entry['employee_name'] = str(first_name) + ' ' + str(last_name)
		new_entry['date_of_birth'] = date_of_birth
		new_entry['joined_system'] = joined_system
		new_entry['street'] = street
		new_entry['city'] = city
		new_entry['state'] = state
		new_entry['zip'] = zip_code
		new_entry['number_of_banks'] = work_for_data.count()
		new_entry['bank_assets'] = employee_assets
		
		joined_table.append(new_entry)

	context = {'joined_table': joined_table}
	return render(request, 'bank/display_employee_stats.html', context)

@never_cache
def hire_employee(request):
	cache.clear()
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = HireEmployeeForm(request.POST, employees=get_Employees(), banks=get_Banks())
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			if len(Bank.objects.filter(manager_id = form.cleaned_data['perID'])) == 0:
				work_for_employee , created= Workfor.objects.get_or_create(
					bankid = Bank.objects.get(pk = form.cleaned_data['bankID']), 
					perid = Employee.objects.get(pk=form.cleaned_data['perID']))
				if created is True:
					messages.success(request, 'Employee Hired!')
				else:
					messages.error(request, 'Key already exists.')
				employee = Employee.objects.filter(pk=form.cleaned_data['perID']).update(salary=form.cleaned_data['salary'])
			else:
				messages.error(request, 'Employee cannot be existing manager.')
				
	# if a GET (or any other method) we'll create a blank form
	else:
		form = HireEmployeeForm(employees=get_Employees(), banks=get_Banks())

	return render(request, 'bank/hire_employee.html', {'form': form})

@never_cache
def replace_manager(request):
	cache.clear()
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = ReplaceManagerForm(request.POST, employees=get_Employees(), banks=get_Banks())
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			if len(Bank.objects.filter(manager_id = form.cleaned_data['perID'])) == 0:
				if len(Workfor.objects.filter(perid = form.cleaned_data['perID'])) == 0:
					bank = Bank.objects.filter(pk=form.cleaned_data['bankID']).update(manager=Employee.objects.get(pk=form.cleaned_data['perID']))
					employee = Employee.objects.filter(pk=form.cleaned_data['perID']).update(salary=form.cleaned_data['salary'])
					messages.success(request, 'Manager Replaced!')
				else:
					messages.error(request, 'Employee cannot be existing worker.')
			else:
				messages.error(request, 'Employee cannot be existing manager.')
				
	# if a GET (or any other method) we'll create a blank form
	else:
		form = ReplaceManagerForm(employees=get_Employees(), banks=get_Banks())

	return render(request, 'bank/replace_manager.html', {'form': form})


@never_cache
def account_withdrawal(request):
	cache.clear()
	if request.session['perID'] is not None and request.session['isCustomer']:
		if request.method == 'POST':
			# create a form instance and populate it with data from the request:
			form = AccountWithdrawalForm(request.POST, banks=get_Banks(), accounts=get_Accounts())
			# check whether it's valid:
			if form.is_valid():
				# process the data in form.cleaned_data as required
				# ...
				# redirect to a new URL:
				bankID = form.cleaned_data['bankID']
				accountID = form.cleaned_data['accountID']
				amount = form.cleaned_data['amount']

				perID = request.session['perID']

				if len(Access.objects.filter(bankid = bankID, accountid = accountID, perid = perID)) == 0:
					messages.error(request, "Person does not have access")

				elif is_checking(bankID, accountID):
					balance = BankAccount.objects.get(bankid = bankID, accountid = accountID).balance or 0
					overdraft_balance = Checking.objects.get(bankid = bankID, accountid = accountID).amount or 0
					print(overdraft_balance)
					if amount > (balance + overdraft_balance):
						messages.error(request, 'Withdrawal amount cant be greater than balance checking amount plus overdraft balance')
					elif amount > balance:
						print("I am here")
						BankAccount.objects.filter(bankid = bankID, accountid = accountID).update(balance = 0)
						overdraft_bank = Checking.objects.get(bankid = bankID, accountid = accountID).protectionbank
						overdraft_account = Checking.objects.get(bankid = bankID, accountid = accountID).protectionaccount
						saving_account_balance = BankAccount.objects.filter(bankid = overdraft_bank, accountid = overdraft_account).balance
						BankAccount.objects.filter(bankid = overdraft_bank, accountid = overdraft_account).update(balance = saving_account_balance - (amount - balance))
						current_date_time = datetime.datetime.now()
						Access.objects.filter(bankid = bankID, accountid = accountID).update(dtaction = current_date_time)
						Checking.objects.filter(bankid = bankID, accountid = accountID).update(dtoverdraft = current_date_time)
						messages.success(request, "Withdrew Amount from Checking + Overdraft")
					else:
						BankAccount.objects.filter(bankid = bankID, accountid = accountID).update(balance = balance - amount)
						current_date_time = datetime.datetime.now()
						Access.objects.filter(bankid = bankID, accountid = accountID).update(dtaction = current_date_time)
						messages.success(request, "Withdrew Amount")
				else:
					balance = BankAccount.objects.get(bankid = bankID, accountid = accountID).balance or 0
					if amount > balance:
						messages.error(request, 'Withdrawal amount cant be greater than balance saving/market account')
					else:
						
						if len(Market.objects.filter(bankid = bankID, accountid = accountID)) > 0:
							numwithdrawals = Market.objects.get(bankid = bankID, accountid = accountID).numwithdrawals
							if Market.objects.get(bankid = bankID, accountid = accountID).maxwithdrawals ==  numwithdrawals:
								messages.error(request, 'Max Withdrawals Reached')
							else:
								Market.objects.filter(bankid = bankID, accountid = accountID).update(numwithdrawals = numwithdrawals + 1)
								BankAccount.objects.filter(bankid = bankID, accountid = accountID).update(balance = balance - (amount))
								current_date_time = datetime.datetime.now()
								Access.objects.filter(bankid = bankID, accountid = accountID).update(dtaction = current_date_time)
						else:
							BankAccount.objects.filter(bankid = bankID, accountid = accountID).update(balance = balance - (amount))
							current_date_time = datetime.datetime.now()
							Access.objects.filter(bankid = bankID, accountid = accountID).update(dtaction = current_date_time)
			else:
				messages.error(request, "Invalid Form")

		# if a GET (or any other method) we'll create a blank form
		else:
			form = AccountWithdrawalForm(banks=get_Banks(), accounts=get_Accounts())

		return render(request, 'bank/account_withdrawal.html', {'form': form})
	else:
		messages.error(request, 'Access Denied.')
		return redirect('/bank/index')
