from django.shortcuts import render
import importlib
from django.http import HttpResponse

# Create your views here.
from .forms import CreateCorporationForm, CreateBankForm
from bank.models import Corporation, Bank


# Queries 3-7, 11
from .forms import CreateEmployeeRoleForm, CreateCustomerRoleForm, StopEmployeeRoleForm, StopCustomerRoleForm, CreateFeeForm
from bank.models import Employee, Customer, InterestBearingFees, InterestBearing, SystemAdmin, BankUser, Workfor, Person, Access, CustomerContacts

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
 
 
##### 3 #####
def create_employee_role(request):
    if request.method == 'POST':
        form = CreateEmployeeRoleForm(request.POST)
        if form.is_valid():
   
            # IF NOT EXISTS (SELECT * FROM employee WHERE perID = ip_perID) and not EXISTS (SELECT * FROM system_admin WHERE perID = ip_perID)
            #     if NOT EXISTS (SELECT * FROM person WHERE perID = ip_perID)
            # ELSEIF EXISTS (SELECT * FROM customer WHERE perID = ip_perID)

            formPerID = form.cleaned_data['perID']
            if len(Employee.objects.filter(perid = formPerID)) == 0 and len(SystemAdmin.objects.filter(perid = formPerID)) == 0:
                if len(Person.objects.filter(perid = formPerID)) == 0:
                    
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

            elif len(Customer.objects.filter(perid = formPerID)) > 0:
                new_employee_role = Employee(
                    perid = form.cleaned_data['perID'],
                    salary = form.cleaned_data['salary'],
                    payments = form.cleaned_data['payments'],
                    earned = form.cleaned_data['earned'])
                new_employee_role.save()
                
                return HttpResponse(status=200)
    else:
        form = CreateEmployeeRoleForm()
    return render(request, 'bank/create_employee_role.html', {'form': form})

##### 4 #####
def create_customer_role(request):
    if request.method == 'POST':
        form = CreateCustomerRoleForm(request.POST)
        if form.is_valid():
            
            # If the person exists as an admin or customer then don't change the database state [not allowed to be admin along with any other person-based role]
            
            # If the person exists as an employee then the customer data is added to create the joint customer-employee role
            
            # If the person doesn't exist then this stored procedure creates a new customer
            
            # if not exists(select * from system_admin where perID = ip_perID) and not exists(select * from customer where perID = ip_perID) then 
            # if EXISTS(SELECT * from employee where perID = ip_perID) THEN 

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
        form = CreateCustomerRoleForm()
        
    return render(request, 'bank/create_customer_role.html', {'form': form})

## SCREEN 5 ##
##### 5 #####
def stop_employee_and_customer_role(request):
    if request.method == 'POST':
        form1 = StopEmployeeRoleForm(request.POST)
        form2 = StopCustomerRoleForm(request.POST)
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
                
                # TODO                
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
        form1 = StopEmployeeRoleForm()
        form2 = StopCustomerRoleForm()
        
    return render(request, 'bank/stop_employee_and_customer_role.html', {'form1': form1, 'form2': form2})


#### SCREEN 9, QUERY 11
def create_fee(request):
    if request.method == 'POST':
        form = CreateFeeForm(request.POST)
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
        form = CreateFeeForm()
        
    return render(request, 'bank/create_fee.html', {'form': form})

