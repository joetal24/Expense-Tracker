from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),
    path('loans/', views.loans, name='loans'),
    path('kaithhealthcheck', views.healthcheck, name='healthcheck'),
    path('kaithheathcheck', views.healthcheck, name='heathcheck_typo'),
]
