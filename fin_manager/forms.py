from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Budget, Transaction


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'amount', 'due_date', 'notes']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0.')
        return amount


class LoanForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['name', 'amount', 'interest_rate', 'due_date', 'notes']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_interest_rate(self):
        rate = self.cleaned_data.get('interest_rate')
        if rate is not None and rate < 0:
            raise forms.ValidationError('Interest rate cannot be negative.')
        return rate


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'name',
            'category',
            'amount',
            'period',
            'start_date',
            'end_date',
            'alert_threshold',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('End date must be on or after start date.')
        return cleaned_data

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Budget amount must be greater than 0.')
        return amount
