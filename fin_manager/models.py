from django.db import models


class Account(models.Model):
    name = models.CharField(max_length=100)
    balance = models.FloatField(default=0)
    income = models.FloatField(default=0)
    expense = models.FloatField(default=0)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    saving_goal = models.FloatField(default=0)
    subscription_list = models.ManyToManyField('Subscription', blank=True)
    liability_list = models.ManyToManyField('Liability', blank=True)
    investment_list = models.ManyToManyField('Investments', blank=True)

class Investments(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    interest_rate = models.FloatField(default=0)
    end_date = models.DateField()
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    

class Liability(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    interest_rate = models.FloatField(default=0)
    is_loan = models.BooleanField(default=False)
    end_date = models.DateField()
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class Subscription(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    end_date = models.DateField()
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
