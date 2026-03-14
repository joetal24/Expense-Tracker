from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Account(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='finance_account')
    name = models.CharField(max_length=120)
    currency = models.CharField(max_length=3, default='UGX')
    monthly_budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    savings_target = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class TransactionQuerySet(models.QuerySet):
    def expenses(self):
        return self.filter(kind=Transaction.Kind.EXPENSE)

    def incomes(self):
        return self.filter(kind=Transaction.Kind.INCOME)

    def loans(self):
        return self.filter(kind=Transaction.Kind.LOAN)

    def in_period(self, start_date, end_date):
        return self.filter(due_date__range=(start_date, end_date))

    def total_amount(self):
        total = self.aggregate(total=Sum('amount'))['total']
        return total or Decimal('0.00')


class Transaction(models.Model):
    class Kind(models.TextChoices):
        EXPENSE = 'expense', 'Expense'
        INCOME = 'income', 'Income'
        LOAN = 'loan', 'Loan'

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    name = models.CharField(max_length=140)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    due_date = models.DateField(db_index=True)
    kind = models.CharField(max_length=12, choices=Kind.choices, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TransactionQuerySet.as_manager()

    class Meta:
        ordering = ['-due_date', '-created_at']
        indexes = [
            models.Index(fields=['account', 'kind', 'due_date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.kind})"
