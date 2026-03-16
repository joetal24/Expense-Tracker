from collections import defaultdict

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import DeleteView, UpdateView
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
    expense_points = [
        dashboard['totals']['weekly']['expenses'],
        dashboard['totals']['monthly']['expenses'],
        dashboard['totals']['yearly']['expenses'],
    ]
    loan_points = [
        dashboard['totals']['weekly']['loans'],
        dashboard['totals']['monthly']['loans'],
        dashboard['totals']['yearly']['loans'],
    ]
    combined_points = [
        dashboard['totals']['weekly']['combined'],
        dashboard['totals']['monthly']['combined'],
        dashboard['totals']['yearly']['combined'],
    ]

    context = {
        'user': request.user,
        'account': account,
        'totals': dashboard['totals'],
        'periods': dashboard['periods'],
        'chart_labels': ['Weekly', 'Monthly', 'Yearly'],
        'chart_expenses': expense_points,
        'chart_loans': loan_points,
        'chart_combined': combined_points,
        'chart_max_expenses': max(expense_points) if any(expense_points) else 1,
        'chart_max_loans': max(loan_points) if any(loan_points) else 1,
        'chart_max_combined': max(combined_points) if any(combined_points) else 1,
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
    success_url = reverse_lazy('expenses')

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
class ExpenseUpdateView(UpdateView):
    model = Transaction
    form_class = ExpenseForm
    template_name = 'expenses/expense_edit.html'
    success_url = reverse_lazy('expenses')

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            kind=Transaction.Kind.EXPENSE,
        )

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.kind = Transaction.Kind.EXPENSE
        transaction.interest_rate = None
        transaction.save()
        return super().form_valid(form)


@method_decorator(login_required(login_url='login'), name='dispatch')
class ExpenseDeleteView(DeleteView):
    model = Transaction
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expenses')

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            kind=Transaction.Kind.EXPENSE,
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class LoanListView(FormView):
    template_name = 'fin_manager/loans.html'
    form_class = LoanForm
    success_url = reverse_lazy('loans')

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


@method_decorator(login_required(login_url='login'), name='dispatch')
class LoanUpdateView(UpdateView):
    model = Transaction
    form_class = LoanForm
    template_name = 'fin_manager/loan_edit.html'
    success_url = reverse_lazy('loans')

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            kind=Transaction.Kind.LOAN,
        )

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.kind = Transaction.Kind.LOAN
        transaction.save()
        return super().form_valid(form)


@method_decorator(login_required(login_url='login'), name='dispatch')
class LoanDeleteView(DeleteView):
    model = Transaction
    template_name = 'fin_manager/loan_confirm_delete.html'
    success_url = reverse_lazy('loans')

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            kind=Transaction.Kind.LOAN,
        )


def healthcheck(request):
    return HttpResponse('ok', content_type='text/plain')
