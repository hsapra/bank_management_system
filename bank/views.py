from django.shortcuts import render
import importlib
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast

# Create your views here.
from .forms import CreateCorporationForm, CreateBankForm, get_Persons
from bank.models import *

def get_url_names():
	from django.apps import apps

	list_of_url_names = list()
	list_of_all_urls = list()
	for name, app in apps.app_configs.items():
		print(name)
		mod_to_import = f'{name}.urls'
		print(mod_to_import)
		try:
			urls = getattr(importlib.import_module(mod_to_import), "urlpatterns")
			print(urls)
			list_of_all_urls.extend(urls)
		except ImportError as ex:
			# is an app without urls
			print("Hello")
			pass
	for url in list_of_all_urls:
		list_of_url_names.append((url.name, url.pattern))

	print(list_of_url_names)
	return list_of_url_names

def index(request):
	context = {'data': get_url_names()}
	return render(request, 'bank/index.html', context)

def create_corporation(request):
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateCorporationForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			new_corp = Corporation(corpid = form.cleaned_data['corpID'], shortname = form.cleaned_data['shortName'], longname = form.cleaned_data['longName'], resassets = form.cleaned_data['resAssets'])
			new_corp.save()
			return HttpResponse(status=200)

	# if a GET (or any other method) we'll create a blank form
	else:
		form = CreateCorporationForm()

	return render(request, 'bank/create_corporation.html', {'form': form})

def create_bank(request):
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateBankForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
			managerId = form.cleaned_data['manager']

			if len(Bank.objects.filter(manager_id = managerId)) == 0:
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
			return HttpResponse(status=200)

	# if a GET (or any other method) we'll create a blank form
	else:
		form = CreateBankForm()

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