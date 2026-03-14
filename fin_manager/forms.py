from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Transaction


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
