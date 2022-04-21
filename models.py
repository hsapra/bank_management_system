# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Access(models.Model):
    perid = models.ForeignKey('Customer', models.DO_NOTHING, db_column='perID')  # Field name made lowercase.
    bankid = models.OneToOneField('BankAccount', models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    accountid = models.ForeignKey('BankAccount', models.DO_NOTHING, db_column='accountID')  # Field name made lowercase.
    dtsharestart = models.DateField(db_column='dtShareStart')  # Field name made lowercase.
    dtaction = models.DateField(db_column='dtAction', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'access'
        unique_together = (('bankid', 'perid', 'accountid'),)


class Bank(models.Model):
    bankid = models.CharField(db_column='bankID', primary_key=True, max_length=100)  # Field name made lowercase.
    bankname = models.CharField(db_column='bankName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=5, blank=True, null=True)
    resassets = models.IntegerField(db_column='resAssets', blank=True, null=True)  # Field name made lowercase.
    corpid = models.ForeignKey('Corporation', models.DO_NOTHING, db_column='corpID')  # Field name made lowercase.
    manager = models.OneToOneField('Employee', models.DO_NOTHING, db_column='manager')

    class Meta:
        managed = False
        db_table = 'bank'
        unique_together = (('street', 'city', 'state', 'zip'),)


class BankAccount(models.Model):
    bankid = models.OneToOneField(Bank, models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    accountid = models.CharField(db_column='accountID', max_length=100)  # Field name made lowercase.
    balance = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bank_account'
        unique_together = (('bankid', 'accountid'),)


class BankUser(models.Model):
    perid = models.OneToOneField('Person', models.DO_NOTHING, db_column='perID', primary_key=True)  # Field name made lowercase.
    taxid = models.CharField(db_column='taxID', unique=True, max_length=11)  # Field name made lowercase.
    birthdate = models.DateField(blank=True, null=True)
    firstname = models.CharField(db_column='firstName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    dtjoined = models.DateField(db_column='dtJoined', blank=True, null=True)  # Field name made lowercase.
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bank_user'


class Checking(models.Model):
    bankid = models.OneToOneField(BankAccount, models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    accountid = models.ForeignKey(BankAccount, models.DO_NOTHING, db_column='accountID')  # Field name made lowercase.
    protectionbank = models.ForeignKey('Savings', models.DO_NOTHING, db_column='protectionBank', blank=True, null=True)  # Field name made lowercase.
    protectionaccount = models.ForeignKey('Savings', models.DO_NOTHING, db_column='protectionAccount', blank=True, null=True)  # Field name made lowercase.
    amount = models.IntegerField(blank=True, null=True)
    dtoverdraft = models.DateField(db_column='dtOverdraft', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'checking'
        unique_together = (('bankid', 'accountid'), ('protectionbank', 'protectionaccount'),)


class Corporation(models.Model):
    corpid = models.CharField(db_column='corpID', primary_key=True, max_length=100)  # Field name made lowercase.
    shortname = models.CharField(db_column='shortName', unique=True, max_length=100)  # Field name made lowercase.
    longname = models.CharField(db_column='longName', unique=True, max_length=100)  # Field name made lowercase.
    resassets = models.IntegerField(db_column='resAssets', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'corporation'


class Customer(models.Model):
    perid = models.OneToOneField(BankUser, models.DO_NOTHING, db_column='perID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customer'


class CustomerContacts(models.Model):
    perid = models.OneToOneField(Customer, models.DO_NOTHING, db_column='perID', primary_key=True)  # Field name made lowercase.
    contact_type = models.CharField(max_length=100)
    info = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'customer_contacts'
        unique_together = (('perid', 'contact_type', 'info'),)


class Employee(models.Model):
    perid = models.OneToOneField(BankUser, models.DO_NOTHING, db_column='perID', primary_key=True)  # Field name made lowercase.
    salary = models.IntegerField(blank=True, null=True)
    payments = models.IntegerField(blank=True, null=True)
    earned = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee'


class InterestBearing(models.Model):
    bankid = models.OneToOneField(BankAccount, models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    accountid = models.ForeignKey(BankAccount, models.DO_NOTHING, db_column='accountID')  # Field name made lowercase.
    interest_rate = models.IntegerField(blank=True, null=True)
    dtdeposit = models.DateField(db_column='dtDeposit', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'interest_bearing'
        unique_together = (('bankid', 'accountid'),)


class InterestBearingFees(models.Model):
    bankid = models.OneToOneField(InterestBearing, models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    accountid = models.ForeignKey(InterestBearing, models.DO_NOTHING, db_column='accountID')  # Field name made lowercase.
    fee = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'interest_bearing_fees'
        unique_together = (('bankid', 'accountid', 'fee'),)


class Market(models.Model):
    bankid = models.OneToOneField(InterestBearing, models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    accountid = models.ForeignKey(InterestBearing, models.DO_NOTHING, db_column='accountID')  # Field name made lowercase.
    maxwithdrawals = models.IntegerField(db_column='maxWithdrawals', blank=True, null=True)  # Field name made lowercase.
    numwithdrawals = models.IntegerField(db_column='numWithdrawals', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'market'
        unique_together = (('bankid', 'accountid'),)


class Person(models.Model):
    perid = models.CharField(db_column='perID', primary_key=True, max_length=100)  # Field name made lowercase.
    pwd = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'person'


class Savings(models.Model):
    bankid = models.OneToOneField(InterestBearing, models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    accountid = models.ForeignKey(InterestBearing, models.DO_NOTHING, db_column='accountID')  # Field name made lowercase.
    minbalance = models.IntegerField(db_column='minBalance', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'savings'
        unique_together = (('bankid', 'accountid'),)


class SystemAdmin(models.Model):
    perid = models.OneToOneField(Person, models.DO_NOTHING, db_column='perID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'system_admin'


class Workfor(models.Model):
    bankid = models.OneToOneField(Bank, models.DO_NOTHING, db_column='bankID', primary_key=True)  # Field name made lowercase.
    perid = models.ForeignKey(Employee, models.DO_NOTHING, db_column='perID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'workFor'
        unique_together = (('bankid', 'perid'),)
