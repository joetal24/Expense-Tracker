from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),
    path('loans/', views.LoanListView.as_view(), name='loans'),
    path('healthz/', views.healthcheck, name='healthcheck'),
    path('healthz', views.healthcheck, name='healthcheck_no_slash'),
    path('kaithhealthcheck/', views.healthcheck, name='kaithhealthcheck'),
    path('kaithhealthcheck', views.healthcheck, name='kaithhealthcheck_no_slash'),
    path('kaithheathcheck/', views.healthcheck, name='kaithheathcheck'),
    path('kaithheathcheck', views.healthcheck, name='kaithheathcheck_no_slash'),
]
