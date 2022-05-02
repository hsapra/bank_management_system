# Bank Management System

Bank Management System is a platform created for CS 4400. It allows seamless communication between the user and the bank_management database.

## Set Up

Start by first setting up the MySQL database by following the steps on CS4400 Canvas. You should have a database called `bank_management`. You should also be aware of your username and password for the MySQL server.

```bash
pip install mysqlclient
```

If you are on Mac you can follow this [InstallationGuide](https://stackoverflow.com/questions/43612243/install-mysqlclient-for-django-python-on-mac-os-x-sierra)

Also set up [django](https://docs.djangoproject.com/en/4.0/topics/install/)

Clone this repository, and navigate into it. Run this 
```bash
pip install -r requirements.txt
```

## Credential Chages

Navigate to `settings.py` in the inner poorly named `bank_managemtent_system` folder and change the following file

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bank_management',
        'USER': #your username,
        'PASSWORD': #your password,
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Usage

```bash
python manage.py runserver
```

Navigate to `127.0.0.1:8000/bank` and see if runs and shows you a list of URLs available.

Enjoy :)

## Team 
Hritik Sapra
Aazia Azmi
Allison Lee
Kaiwen Wang

## License
[MIT](https://choosealicense.com/licenses/mit/)
