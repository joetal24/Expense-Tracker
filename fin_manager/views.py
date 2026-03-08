from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Account, Liability
from .forms import ExpenseForm, LoanForm
from django.views.generic.edit import FormView


# Create your views here.

# @login_required(login_url='/signin')

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'fin_manager/home.html', {'user': request.user})

    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    month_start = today.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)

    year_start = today.replace(month=1, day=1)
    year_end = today.replace(month=12, day=31)

    user_liabilities = Liability.objects.filter(user=request.user)
    expense_qs = user_liabilities.filter(is_loan=False)
    loan_qs = user_liabilities.filter(is_loan=True)

    def sum_for_period(queryset, start_date, end_date):
        total = queryset.filter(end_date__range=(start_date, end_date)).aggregate(total=Sum('amount'))['total']
        return total or 0

    totals = {
        'weekly': {
            'expenses': sum_for_period(expense_qs, week_start, week_end),
            'loans': sum_for_period(loan_qs, week_start, week_end),
        },
        'monthly': {
            'expenses': sum_for_period(expense_qs, month_start, month_end),
            'loans': sum_for_period(loan_qs, month_start, month_end),
        },
        'yearly': {
            'expenses': sum_for_period(expense_qs, year_start, year_end),
            'loans': sum_for_period(loan_qs, year_start, year_end),
        },
    }

    periods = {
        'weekly': f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}",
        'monthly': f"{month_start.strftime('%b %d')} - {month_end.strftime('%b %d, %Y')}",
        'yearly': f"{year_start.strftime('%b %d')} - {year_end.strftime('%b %d, %Y')}",
    }

    context = {
        'user': request.user,
        'totals': totals,
        'periods': periods,
    }
    return render(request, 'fin_manager/home.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in
            login(request, user)
            return redirect('home')  # Change 'home' to your desired URL
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def loans(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            account, _ = Account.objects.get_or_create(
                user=request.user,
                defaults={'name': f'{request.user.username} Account'}
            )

            liability = Liability(
                name=form.cleaned_data['name'],
                amount=form.cleaned_data['amount'],
                interest_rate=form.cleaned_data['interest_rate'],
                is_loan=True,
                end_date=form.cleaned_data['end_date'],
                user=request.user
            )
            liability.save()
            account.liability_list.add(liability)
            return redirect('loans')
    else:
        form = LoanForm()

    user_loans = Liability.objects.filter(user=request.user, is_loan=True)
    return render(request, 'fin_manager/loans.html', {'loans': user_loans, 'form': form})


def healthcheck(request):
    return HttpResponse('ok', content_type='text/plain')


class ExpenseListView(FormView):
    template_name = 'expenses/expense_list.html'
    form_class = ExpenseForm
    success_url = '/expenses/'  # Update this with the correct URL

    def form_valid(self, form):
        # Retrieve the user's account
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Account'}
        )
        
        # Create a new liability instance and link it to the user's account
        liability = Liability(
            name=form.cleaned_data['name'],
            amount=form.cleaned_data['amount'],
            is_loan=False,
            end_date=form.cleaned_data['end_date'],
            user=self.request.user
        )
        liability.save()
        account.liability_list.add(liability)
        return super().form_valid(form)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Retrieve user's account data and related liabilities
        accounts = Account.objects.filter(user=user)
        print(accounts)
        # Create a dictionary to store expense data grouped by month
        expense_data = {}

        for account in accounts:
            liabilities = account.liability_list.filter(is_loan=False)
            for liability in liabilities:
                year_month = liability.end_date.strftime('%Y-%m')

                if year_month not in expense_data:
                    expense_data[year_month] = []

                expense_data[year_month].append({
                    'name': liability.name,
                    'amount': liability.amount,
                    'end_date': liability.end_date,
                })
        
        context['expense_data'] = expense_data
        return context
