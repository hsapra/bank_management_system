from django.shortcuts import render
import importlib
from django.http import HttpResponse

# Create your views here.
from .forms import CreateCorporationForm, CreateBankForm
from bank.models import Corporation, Bank, Employee

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

