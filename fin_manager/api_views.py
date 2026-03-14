from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_serializers import (
    AccountSerializer,
    DashboardSerializer,
    ExpenseSerializer,
    LoanSerializer,
    RegisterSerializer,
    SyncPayloadSerializer,
)
from .models import Account, Transaction


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
                'synced_loans': len(synced_loans),
            }
        )


class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account, _ = Account.objects.get_or_create(
            user=request.user,
            defaults={'name': f'{request.user.username} Main Account'},
        )
        payload = DashboardSerializer.from_account(account)
        return Response(payload)
