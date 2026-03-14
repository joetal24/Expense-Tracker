from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),
    path('loans/', views.LoanListView.as_view(), name='loans'),
    path('healthz/', views.healthcheck, name='healthcheck'),
]
