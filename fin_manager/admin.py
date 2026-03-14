from django.contrib import admin
from .models import Account, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'name', 'currency', 'monthly_budget', 'savings_target')
	search_fields = ('user__username', 'name')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('id', 'account', 'kind', 'name', 'amount', 'interest_rate', 'due_date')
	list_filter = ('kind', 'due_date')
	search_fields = ('name', 'account__user__username')
