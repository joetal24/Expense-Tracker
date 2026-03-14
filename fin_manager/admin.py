from django.contrib import admin
from .models import Account, FCMDevice, Receipt, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'name', 'currency', 'monthly_budget', 'savings_target')
	search_fields = ('user__username', 'name')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('id', 'account', 'kind', 'name', 'amount', 'interest_rate', 'due_date')
	list_filter = ('kind', 'due_date')
	search_fields = ('name', 'account__user__username')


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
	list_display = ('id', 'transaction', 'uploaded_by', 'created_at')
	search_fields = ('uploaded_by__username',)


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'device_name', 'is_active', 'updated_at')
	list_filter = ('is_active',)
	search_fields = ('user__username', 'device_name')
