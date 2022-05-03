from django.shortcuts import render, redirect
import importlib
from django.http import HttpResponse
from django.contrib import messages
import datetime


# Create your views here.
from .forms import *

from bank.models import *

from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.db import IntegrityError
from psycopg2.errorcodes import UNIQUE_VIOLATION

from .forms import CreateEmployeeRoleForm

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


def get_Customers():
    list_of_banks = list(Customer.objects.all().values_list('perid', flat=True).distinct())

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
					if amount > (balance + overdraft_balance):
						messages.error(request, 'Withdrawal amount cant be greater than balance checking amount plus overdraft balance')
					elif amount > balance:
						BankAccount.objects.filter(bankid = bankID, accountid = accountID).update(balance = 0)
						overdraft_bank = Checking.objects.get(bankid = bankID, accountid = accountID).protectionbank
						overdraft_account = Checking.objects.get(bankid = bankID, accountid = accountID).protectionaccount
						saving_account_balance = BankAccount.objects.filter(bankid = overdraft_bank, accountid = overdraft_account).balance
						BankAccount.objects.filter(bankid = overdraft_bank, accountid = overdraft_account).update(balance = saving_account_balance - (amount - balance))
						current_date_time = datetime.datetime.now()
						Access.objects.filter(bankid = bankID, accountid = accountID).update(dtaction = current_date_time)
						Checking.objects.filter(bankid = bankID, accountid = accountID).update(dtoverdraft = current_date_time)
				else:
					BankAccount.objects.filter(bankid = bankID, accountid = accountID).update(balance = balance - amount)
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



##### 3 #####
@never_cache
def create_employee_role(request):
    if request.method == 'POST':
        form = CreateEmployeeRoleForm(request.POST, persons=get_Persons())
        if form.is_valid():

            if len(Employee.objects.filter(perid = form.cleaned_data['perID'])) == 0 and len(SystemAdmin.objects.filter(perid = form.cleaned_data['perID'])) == 0:
                if len(Person.objects.filter(perid = form.cleaned_data['perID'])) == 0:
                    
                    new_person = Person(
                        perid = form.cleaned_data['perID'],
                    )
                    new_person.save()
                    
                    new_bank_user = BankUser(
                        perid = form.cleaned_data['perID'],
                    )
                    new_bank_user.save()
                    
                    new_employee_role = Employee(
                        perid = form.cleaned_data['perID'],
                        salary = form.cleaned_data['salary'],
                        payments = form.cleaned_data['payments'],
                        earned = form.cleaned_data['earned'])
                    new_employee_role.save()
                    
                    return HttpResponse(status=200)

            elif len(Customer.objects.filter(perid = form.cleaned_data['perID'])) > 0:
                new_employee_role = Employee(
                    perid = form.cleaned_data['perID'],
                    salary = form.cleaned_data['salary'],
                    payments = form.cleaned_data['payments'],
                    earned = form.cleaned_data['earned'])
                new_employee_role.save()
                
                return HttpResponse(status=200)
    else:
        form = CreateEmployeeRoleForm(persons=get_Persons())
    return render(request, 'bank/create_employee_role.html', {'form': form})

##### 4 #####
@never_cache
def create_customer_role(request):
    if request.method == 'POST':
        form = CreateCustomerRoleForm(request.POST, perid=get_Customers())
        if form.is_valid():
            
            if len(SystemAdmin.objects.filter(perid = form.cleaned_data['perID'])) == 0 and len(Customer.objects.filter(perid = form.cleaned_data['perID'])) == 0:
                if len(Employee.objects.filter(perid = form.cleaned_data['perID'])) >= 0:
                    new_customer = Customer(
                        perid = form.cleaned_data['perID'],
                    )
                    new_customer.save()
                    
                    new_person = Person(
                        perid = form.cleaned_data['perID'],
                    )
                    new_person.save()
                    
                    new_bankuser = BankUser(
                        perid = form.cleaned_data['perID'],
                    )
                    new_bankuser.save()
                    
                    new_customer = Customer(
                        perid = form.cleaned_data['perID'],
                    )
                    new_customer.save()
                    
                    return HttpResponse(status=200)

    else:
        form = CreateCustomerRoleForm(perid=get_Customers())
        
    return render(request, 'bank/create_customer_role.html', {'form': form})



# SCREEN 5 ##
##### 5 #####
@never_cache
def stop_employee_and_customer_role(request):
    if request.method == 'POST':
        form1 = StopEmployeeRoleForm(request.POST, employee=get_Employees())
        form2 = StopCustomerRoleForm(request.POST, customer=get_Customers())
        if form1.is_valid():

            if len(Employee.objects.filter(perid = form1.cleaned_data['perID'])) >= 1:

                # TODO: Not sure if I should be getting first object or not
                bank_id_var = Workfor.objects.filter(perid = form1.cleaned_data['perID'])
                num_employees_in_bank_var = len(Workfor.objects.filter(perid = form1.cleaned_data['perID']))
                
                manager_var = Bank.objects.filter(bankid = bank_id_var[0].bankid)
                manager_var = manager_var[0].manager
                
                if num_employees_in_bank_var > 1 and manager_var != form1.cleaned_data['perID']:

                    Workfor.objects.filter(perid = form1.cleaned_data['perID']).delete()
                    Employee.objects.filter(perid = form1.cleaned_data['perID']).delete()
                    
                    if len(Customer.objects.filter(perID = form1.cleaned_data['perID'])) == 0:
                                                
                        BankUser.objects.filter(perid = form1.cleaned_data['perID']).delete()
                        Person.objects.filter(perid = form1.cleaned_data['perID']).delete()
                        
                        return HttpResponse(status=200)
                        


        if form2.is_valid():
            if len(Customer.objects.filter(perid = form2.cleaned_data['perID'])) > 0:
                
                # accountId in (select accountID from access group by accountID having count(*) = 1))
                # accountId_list = Access.objects.filter(Access.objects.count(accountid) == 1).values_list('accountid', flat=True)
                # accountID_list = Access.objects.filter(Access.objects.count(accountid) == 1)
                
                # TODO impelment accountId in (select accountID from access group by accountID having count(*) = 1))
                #  I guess you don't need this because there is not an account..? Or do we get the account for the specific person. 
                # accountid_list = Access.objects.filter(Access.objects.count(Access.accountid) == 1).values_list('accountid', flat=True)
                
                if len(Access.objects.filter(perid = form2.cleaned_data['perID'])) == 0:
                    
                    if len(Employee.objects.filter(perid = form2.cleaned_data['perID'])) > 0:
                        Access.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        CustomerContacts.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        Customer.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        return HttpResponse(status=200)
                    else:
                        Access.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        CustomerContacts.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        Customer.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        BankUser.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        Person.objects.filter(perid = form2.cleaned_data['perID']).delete()
                        return HttpResponse(status=200)
    else:
        form1 = StopEmployeeRoleForm(employee=get_Employees())
        form2 = StopCustomerRoleForm(customer=get_Customers())
        
    return render(request, 'bank/stop_employee_and_customer_role.html', {'form1': form1, 'form2': form2})


#### SCREEN 9, QUERY 11
@never_cache
def create_fee(request):
    if request.method == 'POST':
        form = CreateFeeForm(request.POST, meow=get_Banks(), potato=get_Accounts())
        if form.is_valid():
            
            
            # 	if exists (select * from interest_bearing where bankID = ip_bankID and accountID = ip_accountID)
            formBankID = form.cleaned_data['bankID']
            formAccountID = form.cleaned_data['accountID']

            if len(InterestBearing.objects.filter(bankid = formBankID, accountid = formAccountID)) >= 1:
        
            # insert into interest_bearing_fees values (ip_bankID, ip_accountID, ip_fee_type);
                new_interest_fee = InterestBearingFees(
                    bankid = form.cleaned_data['bankID'],
                    accountid = form.cleaned_data['accountID'],
                    fee = form.cleaned_data['feeType']
                )
                new_interest_fee.save()
        
            return HttpResponse(status=200)
    else:
        form = CreateFeeForm(meow=get_Banks(), potato=get_Accounts())
        
    return render(request, 'bank/create_fee.html', {'form': form})

