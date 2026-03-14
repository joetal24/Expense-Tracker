from collections import defaultdict

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from .forms import ExpenseForm, LoanForm, RegisterForm
from .models import Account, Transaction
from .services import build_dashboard_summary

# Create your views here.

# @login_required(login_url='/signin')

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'fin_manager/home.html', {'user': request.user})

    account, _ = Account.objects.get_or_create(
        user=request.user,
        defaults={'name': f'{request.user.username} Main Account'}
    )

    dashboard = build_dashboard_summary(account)

    context = {
        'user': request.user,
        'account': account,
        'totals': dashboard['totals'],
        'periods': dashboard['periods'],
    }
    return render(request, 'fin_manager/home.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Account.objects.get_or_create(
                user=user,
                defaults={'name': f'{user.username} Main Account'}
            )
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@method_decorator(login_required(login_url='login'), name='dispatch')
class ExpenseListView(FormView):
    template_name = 'expenses/expense_list.html'
    form_class = ExpenseForm
    success_url = '/expenses/'

    def form_valid(self, form):
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )

        transaction = form.save(commit=False)
        transaction.account = account
        transaction.kind = Transaction.Kind.EXPENSE
        transaction.interest_rate = None
        transaction.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )

        grouped = defaultdict(list)
        expenses = account.transactions.expenses().order_by('-due_date')

        for expense in expenses:
            key = expense.due_date.strftime('%Y-%m')
            grouped[key].append(expense)

        context['expense_data'] = dict(grouped)
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class LoanListView(FormView):
    template_name = 'fin_manager/loans.html'
    form_class = LoanForm
    success_url = '/loans/'

    def form_valid(self, form):
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )

        transaction = form.save(commit=False)
        transaction.account = account
        transaction.kind = Transaction.Kind.LOAN
        transaction.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )
        context['loans'] = account.transactions.loans().order_by('-due_date')
        return context


def healthcheck(request):
    return HttpResponse('ok', content_type='text/plain')
