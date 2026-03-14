from django.urls import path

from .api_views import (
    AccountAPIView,
    CategoryListAPIView,
    DashboardAPIView,
    ExpenseListCreateAPIView,
    FCMDeviceAPIView,
    IncomeListCreateAPIView,
    LoginAPIView,
    LoanListCreateAPIView,
    MeAPIView,
    ReceiptUploadAPIView,
    ReportMonthlyAPIView,
    ReportTrendsAPIView,
    RefreshTokenAPIView,
    RegisterAPIView,
    SMSParseAPIView,
    SyncAPIView,
)

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/refresh/', RefreshTokenAPIView.as_view(), name='api-refresh'),
    path('auth/me/', MeAPIView.as_view(), name='api-me'),
    path('accounts/', AccountAPIView.as_view(), name='api-account'),
    path('categories/', CategoryListAPIView.as_view(), name='api-categories'),
    path('expenses/', ExpenseListCreateAPIView.as_view(), name='api-expenses'),
    path('income/', IncomeListCreateAPIView.as_view(), name='api-income'),
    path('loans/', LoanListCreateAPIView.as_view(), name='api-loans'),
    path('reports/monthly/', ReportMonthlyAPIView.as_view(), name='api-report-monthly'),
    path('reports/trends/', ReportTrendsAPIView.as_view(), name='api-report-trends'),
    path('dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),
    path('sync/', SyncAPIView.as_view(), name='api-sync'),
    path('receipts/', ReceiptUploadAPIView.as_view(), name='api-receipts'),
    path('fcm/register/', FCMDeviceAPIView.as_view(), name='api-fcm-register'),
    path('sms/parse/', SMSParseAPIView.as_view(), name='api-sms-parse'),
]
