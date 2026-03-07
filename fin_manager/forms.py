from django import forms
from .models import Liability

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = ['name', 'amount', 'end_date']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class LoanForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = ['name', 'amount', 'interest_rate', 'end_date']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
