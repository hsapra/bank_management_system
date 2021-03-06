# Generated by Django 4.0.4 on 2022-04-24 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('bankid', models.CharField(db_column='bankID', max_length=100, primary_key=True, serialize=False)),
                ('bankname', models.CharField(blank=True, db_column='bankName', max_length=100, null=True)),
                ('street', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=2, null=True)),
                ('zip', models.CharField(blank=True, max_length=5, null=True)),
                ('resassets', models.IntegerField(blank=True, db_column='resAssets', null=True)),
            ],
            options={
                'db_table': 'bank',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Corporation',
            fields=[
                ('corpid', models.CharField(db_column='corpID', max_length=100, primary_key=True, serialize=False)),
                ('shortname', models.CharField(db_column='shortName', max_length=100, unique=True)),
                ('longname', models.CharField(db_column='longName', max_length=100, unique=True)),
                ('resassets', models.IntegerField(blank=True, db_column='resAssets', null=True)),
            ],
            options={
                'db_table': 'corporation',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('perid', models.CharField(db_column='perID', max_length=100, primary_key=True, serialize=False)),
                ('pwd', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'person',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.bank')),
                ('accountid', models.CharField(db_column='accountID', max_length=100)),
                ('balance', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'bank_account',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BankUser',
            fields=[
                ('perid', models.OneToOneField(db_column='perID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.person')),
                ('taxid', models.CharField(db_column='taxID', max_length=11, unique=True)),
                ('birthdate', models.DateField(blank=True, null=True)),
                ('firstname', models.CharField(blank=True, db_column='firstName', max_length=100, null=True)),
                ('lastname', models.CharField(blank=True, db_column='lastName', max_length=100, null=True)),
                ('dtjoined', models.DateField(blank=True, db_column='dtJoined', null=True)),
                ('street', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=2, null=True)),
                ('zip', models.CharField(blank=True, max_length=5, null=True)),
            ],
            options={
                'db_table': 'bank_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SystemAdmin',
            fields=[
                ('perid', models.OneToOneField(db_column='perID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.person')),
            ],
            options={
                'db_table': 'system_admin',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Workfor',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.bank')),
            ],
            options={
                'db_table': 'workFor',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Access',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.bankaccount')),
                ('dtsharestart', models.DateField(db_column='dtShareStart')),
                ('dtaction', models.DateField(blank=True, db_column='dtAction', null=True)),
            ],
            options={
                'db_table': 'access',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Checking',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.bankaccount')),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('dtoverdraft', models.DateField(blank=True, db_column='dtOverdraft', null=True)),
            ],
            options={
                'db_table': 'checking',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('perid', models.OneToOneField(db_column='perID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.bankuser')),
            ],
            options={
                'db_table': 'customer',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('perid', models.OneToOneField(db_column='perID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.bankuser')),
                ('salary', models.IntegerField(blank=True, null=True)),
                ('payments', models.IntegerField(blank=True, null=True)),
                ('earned', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'employee',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='InterestBearing',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.bankaccount')),
                ('interest_rate', models.IntegerField(blank=True, null=True)),
                ('dtdeposit', models.DateField(blank=True, db_column='dtDeposit', null=True)),
            ],
            options={
                'db_table': 'interest_bearing',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CustomerContacts',
            fields=[
                ('perid', models.OneToOneField(db_column='perID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.customer')),
                ('contact_type', models.CharField(max_length=100)),
                ('info', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'customer_contacts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='InterestBearingFees',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.interestbearing')),
                ('fee', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'interest_bearing_fees',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.interestbearing')),
                ('maxwithdrawals', models.IntegerField(blank=True, db_column='maxWithdrawals', null=True)),
                ('numwithdrawals', models.IntegerField(blank=True, db_column='numWithdrawals', null=True)),
            ],
            options={
                'db_table': 'market',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Savings',
            fields=[
                ('bankid', models.OneToOneField(db_column='bankID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='bank.interestbearing')),
                ('minbalance', models.IntegerField(blank=True, db_column='minBalance', null=True)),
            ],
            options={
                'db_table': 'savings',
                'managed': False,
            },
        ),
    ]
