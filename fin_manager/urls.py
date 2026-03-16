from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),
    path('expenses/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    path('loans/', views.LoanListView.as_view(), name='loans'),
    path('loans/<int:pk>/edit/', views.LoanUpdateView.as_view(), name='loan_edit'),
    path('loans/<int:pk>/delete/', views.LoanDeleteView.as_view(), name='loan_delete'),
    path('budgets/', views.BudgetListView.as_view(), name='budgets'),
    path('budgets/<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
    path('reports/', views.reports, name='reports'),
    path('healthz/', views.healthcheck, name='healthcheck'),
    path('healthz', views.healthcheck, name='healthcheck_no_slash'),
    path('kaithhealthcheck/', views.healthcheck, name='kaithhealthcheck'),
    path('kaithhealthcheck', views.healthcheck, name='kaithhealthcheck_no_slash'),
    path('kaithheathcheck/', views.healthcheck, name='kaithheathcheck'),
    path('kaithheathcheck', views.healthcheck, name='kaithheathcheck_no_slash'),
]
