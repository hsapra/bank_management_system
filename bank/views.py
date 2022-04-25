from django.shortcuts import render
import importlib
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.
from .forms import CreateCorporationForm, CreateBankForm
from bank.models import Corporation, Bank, Employee, Workfor
from django.views.decorators.cache import never_cache

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

@never_cache
def create_corporation(request):
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
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateBankForm(request.POST)
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
					else:
						messages.error(request, 'Existing Bank.')
				else:
					messages.error(request, 'Employee cannot be existing manager.')
			else:
				messages.error(request, 'Manager cannot be existing manager.')
				
	# if a GET (or any other method) we'll create a blank form
	else:
		form = CreateBankForm()

	return render(request, 'bank/create_bank.html', {'form': form})

