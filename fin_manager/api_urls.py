from django.urls import path

from .api_views import (
    AccountAPIView,
    DashboardAPIView,
    ExpenseListCreateAPIView,
    LoginAPIView,
    LoanListCreateAPIView,
    MeAPIView,
    RefreshTokenAPIView,
    RegisterAPIView,
    SyncAPIView,
)

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/refresh/', RefreshTokenAPIView.as_view(), name='api-refresh'),
    path('auth/me/', MeAPIView.as_view(), name='api-me'),
    path('accounts/', AccountAPIView.as_view(), name='api-account'),
    path('expenses/', ExpenseListCreateAPIView.as_view(), name='api-expenses'),
    path('loans/', LoanListCreateAPIView.as_view(), name='api-loans'),
    path('dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),
    path('sync/', SyncAPIView.as_view(), name='api-sync'),
]
