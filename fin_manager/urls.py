from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),
    path('loans/', views.loans, name='loans'),
]
