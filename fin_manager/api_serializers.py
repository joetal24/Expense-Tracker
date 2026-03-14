from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Account, Transaction
from .services import build_dashboard_summary


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        Account.objects.get_or_create(user=user, defaults={'name': f'{user.username} Main Account'})
        return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'currency', 'monthly_budget', 'savings_target', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'name',
            'amount',
            'interest_rate',
            'due_date',
            'kind',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseSerializer(TransactionSerializer):
    class Meta(TransactionSerializer.Meta):
        extra_kwargs = {
            'kind': {'read_only': True},
            'interest_rate': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        attrs['kind'] = Transaction.Kind.EXPENSE
        attrs['interest_rate'] = None
        return attrs


class LoanSerializer(TransactionSerializer):
    class Meta(TransactionSerializer.Meta):
        extra_kwargs = {
            'kind': {'read_only': True},
            'interest_rate': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        attrs['kind'] = Transaction.Kind.LOAN
        return attrs


class SyncPayloadSerializer(serializers.Serializer):
    expenses = ExpenseSerializer(many=True, required=False)
    loans = LoanSerializer(many=True, required=False)


class DashboardSerializer(serializers.Serializer):
    periods = serializers.DictField(child=serializers.CharField())
    totals = serializers.DictField()

    @staticmethod
    def from_account(account):
        return build_dashboard_summary(account)
