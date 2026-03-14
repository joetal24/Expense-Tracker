from datetime import date

from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_serializers import (
    AccountSerializer,
    CategorySerializer,
    DashboardSerializer,
    ExpenseSerializer,
    FCMDeviceSerializer,
    IncomeSerializer,
    LoanSerializer,
    ReceiptSerializer,
    RegisterSerializer,
    SyncPayloadSerializer,
)
from .models import Account, FCMDevice, Receipt, Transaction
from .sms_parser import MoMoSMSParser


DEFAULT_CATEGORIES = [
    {'id': 'transport', 'name': 'Transport', 'category_type': 'expense'},
    {'id': 'food', 'name': 'Food', 'category_type': 'expense'},
    {'id': 'housing', 'name': 'Housing', 'category_type': 'expense'},
    {'id': 'utilities', 'name': 'Utilities', 'category_type': 'expense'},
    {'id': 'health', 'name': 'Health', 'category_type': 'expense'},
    {'id': 'salary', 'name': 'Salary', 'category_type': 'income'},
    {'id': 'business', 'name': 'Business', 'category_type': 'income'},
    {'id': 'farming', 'name': 'Farming', 'category_type': 'income'},
    {'id': 'other', 'name': 'Other', 'category_type': 'both'},
]


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class RefreshTokenAPIView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )
        return Response(
            {
                'id': request.user.id,
                'username': request.user.username,
                'account': AccountSerializer(account).data,
            }
        )


class AccountAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'},
        )
        return account


class CategoryListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CategorySerializer(DEFAULT_CATEGORIES, many=True)
        return Response(serializer.data)


class ExpenseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'},
        )
        return account.transactions.expenses().order_by('-due_date', '-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )

        serializer.save(account=account, kind=Transaction.Kind.EXPENSE, interest_rate=None)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LoanListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'},
        )
        return account.transactions.loans().order_by('-due_date', '-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )

        serializer.save(account=account, kind=Transaction.Kind.LOAN)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class IncomeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'},
        )
        return account.transactions.incomes().order_by('-due_date', '-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )

        serializer.save(account=account, kind=Transaction.Kind.INCOME, interest_rate=None)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SyncAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SyncPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )

        synced_expenses = []
        for expense_data in serializer.validated_data.get('expenses', []):
            payload = dict(expense_data)
            payload.pop('kind', None)
            payload.pop('interest_rate', None)
            transaction = Transaction.objects.create(
                account=account,
                kind=Transaction.Kind.EXPENSE,
                interest_rate=None,
                **payload,
            )
            synced_expenses.append(transaction.id)

        synced_incomes = []
        for income_data in serializer.validated_data.get('incomes', []):
            payload = dict(income_data)
            payload.pop('kind', None)
            payload.pop('interest_rate', None)
            transaction = Transaction.objects.create(
                account=account,
                kind=Transaction.Kind.INCOME,
                interest_rate=None,
                **payload,
            )
            synced_incomes.append(transaction.id)

        synced_loans = []
        for loan_data in serializer.validated_data.get('loans', []):
            payload = dict(loan_data)
            payload.pop('kind', None)
            transaction = Transaction.objects.create(
                account=account,
                kind=Transaction.Kind.LOAN,
                **payload,
            )
            synced_loans.append(transaction.id)

        return Response(
            {
                'status': 'synced',
                'synced_expenses': len(synced_expenses),
                'synced_incomes': len(synced_incomes),
                'synced_loans': len(synced_loans),
            }
        )


class ReportMonthlyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )

        today = timezone.localdate()
        year = int(request.query_params.get('year', today.year))
        month = int(request.query_params.get('month', today.month))

        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)

        transactions = account.transactions.filter(due_date__gte=start, due_date__lt=end)
        expenses = transactions.expenses()
        incomes = transactions.incomes()

        total_expense = expenses.total_amount()
        total_income = incomes.total_amount()
        net_savings = total_income - total_expense

        category_breakdown = list(
            expenses.values('name').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')
        )

        daily_totals = list(
            expenses.annotate(day=TruncDay('due_date')).values('day').annotate(total=Sum('amount')).order_by('day')
        )

        savings_rate = 0.0
        if total_income > 0:
            savings_rate = round(float((net_savings / total_income) * 100), 1)

        return Response(
            {
                'year': year,
                'month': month,
                'total_expense': total_expense,
                'total_income': total_income,
                'net_savings': net_savings,
                'savings_rate': savings_rate,
                'category_breakdown': category_breakdown,
                'daily_totals': [
                    {'date': row['day'].isoformat(), 'amount': row['total']} for row in daily_totals
                ],
            }
        )


class ReportTrendsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )

        expenses = list(
            account.transactions.expenses()
            .annotate(month=TruncMonth('due_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        incomes = list(
            account.transactions.incomes()
            .annotate(month=TruncMonth('due_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        expense_by_month = {row['month']: row['total'] for row in expenses}
        income_by_month = {row['month']: row['total'] for row in incomes}
        months = sorted(set(expense_by_month.keys()) | set(income_by_month.keys()))[-6:]

        trends = [
            {
                'month': month.strftime('%b %Y'),
                'expenses': expense_by_month.get(month, 0),
                'income': income_by_month.get(month, 0),
            }
            for month in months
        ]

        return Response({'trends': trends})


class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )
        payload = DashboardSerializer.from_account(account)
        return Response(payload)


class ReceiptUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        transaction_id = request.data.get('transaction')
        transaction = None

        if transaction_id:
            account, _ = Account.objects.get_or_create(
                user=request.user,
                defaults={'name': f'{request.user.username} Main Account'},
            )
            try:
                transaction = account.transactions.get(id=transaction_id)
            except Transaction.DoesNotExist:
                return Response({'detail': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReceiptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receipt = serializer.save(uploaded_by=request.user, transaction=transaction)
        return Response(ReceiptSerializer(receipt).data, status=status.HTTP_201_CREATED)


class FCMDeviceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FCMDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device, _ = FCMDevice.objects.update_or_create(
            token=serializer.validated_data['token'],
            defaults={
                'user': request.user,
                'device_name': serializer.validated_data.get('device_name', ''),
                'is_active': serializer.validated_data.get('is_active', True),
            },
        )
        return Response(FCMDeviceSerializer(device).data, status=status.HTTP_201_CREATED)


class SMSParseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sms_text = request.data.get('sms', '')
        if not sms_text:
            return Response({'detail': 'sms is required.'}, status=status.HTTP_400_BAD_REQUEST)

        parsed = MoMoSMSParser.parse(sms_text)
        if parsed:
            return Response({'parsed': True, 'data': parsed})
        return Response({'parsed': False, 'data': None})
