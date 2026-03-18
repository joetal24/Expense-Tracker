import calendar
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.generic import DeleteView, UpdateView
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from .forms import BudgetForm, ExpenseForm, IncomeForm, LoanForm, RegisterForm
from .models import Account, Budget, Transaction
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

    income_points = [
        dashboard['totals']['weekly']['incomes'],
        dashboard['totals']['monthly']['incomes'],
        dashboard['totals']['yearly']['incomes'],
    ]
    net_savings_points = [
        dashboard['totals']['weekly']['net_savings'],
        dashboard['totals']['monthly']['net_savings'],
        dashboard['totals']['yearly']['net_savings'],
    ]
    recent_expenses = account.transactions.expenses().order_by('-due_date', '-created_at')[:5]
    recent_incomes = account.transactions.incomes().order_by('-due_date', '-created_at')[:5]
    recent_loans = account.transactions.loans().order_by('-due_date', '-created_at')[:5]
    context = {
        'user': request.user,
        'account': account,
        'totals': dashboard['totals'],
        'periods': dashboard['periods'],
        'period_list': ['weekly', 'monthly', 'yearly'],
        'chart_labels': ['Weekly', 'Monthly', 'Yearly'],
        'chart_expenses': expense_points,
        'chart_loans': loan_points,
        'chart_combined': combined_points,
        'chart_incomes': income_points,
        'chart_net_savings': net_savings_points,
        'chart_max_expenses': max(expense_points) if any(expense_points) else 1,
        'chart_max_loans': max(loan_points) if any(loan_points) else 1,
        'chart_max_combined': max(combined_points) if any(combined_points) else 1,
        'recent_expenses': recent_expenses,
        'recent_incomes': recent_incomes,
        'recent_loans': recent_loans,
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
        messages.success(self.request, 'Expense added successfully!')
        return super().form_valid(form)

    from django.core.paginator import Paginator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )

        grouped = defaultdict(list)
        expenses = account.transactions.expenses().order_by('-due_date')

        # Flatten all expenses for pagination
        all_expenses = list(expenses)
        paginator = Paginator(all_expenses, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Regroup only the paginated expenses
        for expense in page_obj:
            key = expense.due_date.strftime('%Y-%m')
            grouped[key].append(expense)

        context['expense_data'] = dict(grouped)
        context['page_obj'] = page_obj
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
        messages.success(self.request, 'Expense updated successfully!')
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

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Expense deleted successfully!')
        return super().delete(request, *args, **kwargs)


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
        messages.success(self.request, 'Loan added successfully!')
        return super().form_valid(form)

    from django.core.paginator import Paginator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )
        loans = account.transactions.loans().order_by('-due_date')
        paginator = Paginator(loans, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['loans'] = page_obj
        context['page_obj'] = page_obj
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
        messages.success(self.request, 'Loan updated successfully!')
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

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Loan deleted successfully!')
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required(login_url='login'), name='dispatch')
class IncomeListView(FormView):
    template_name = 'fin_manager/incomes.html'
    form_class = IncomeForm
    success_url = reverse_lazy('incomes')

    def form_valid(self, form):
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )

        transaction = form.save(commit=False)
        transaction.account = account
        transaction.kind = Transaction.Kind.INCOME
        transaction.interest_rate = None
        transaction.save()
        messages.success(self.request, 'Income added successfully!')
        return super().form_valid(form)

    from django.core.paginator import Paginator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )
        incomes = account.transactions.incomes().order_by('-due_date')
        paginator = Paginator(incomes, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['incomes'] = page_obj
        context['page_obj'] = page_obj
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class IncomeUpdateView(UpdateView):
    model = Transaction
    form_class = IncomeForm
    template_name = 'fin_manager/income_edit.html'
    success_url = reverse_lazy('incomes')

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            kind=Transaction.Kind.INCOME,
        )

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.kind = Transaction.Kind.INCOME
        transaction.interest_rate = None
        transaction.save()
        messages.success(self.request, 'Income updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required(login_url='login'), name='dispatch')
class IncomeDeleteView(DeleteView):
    model = Transaction
    template_name = 'fin_manager/income_confirm_delete.html'
    success_url = reverse_lazy('incomes')

    def get_queryset(self):
        return Transaction.objects.filter(
            account__user=self.request.user,
            kind=Transaction.Kind.INCOME,
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Income deleted successfully!')
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required(login_url='login'), name='dispatch')
class BudgetListView(FormView):
    template_name = 'budgets/budget_list.html'
    form_class = BudgetForm
    success_url = reverse_lazy('budgets')

    def form_valid(self, form):
        budget = form.save(commit=False)
        budget.user = self.request.user
        budget.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account, _ = Account.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f'{self.request.user.username} Main Account'}
        )
        budget_items = []

        budgets = Budget.objects.filter(user=self.request.user).order_by('-start_date', '-created_at')
        for budget in budgets:
            tx_qs = account.transactions.expenses().filter(
                due_date__gte=budget.start_date,
                due_date__lte=budget.end_date,
            )
            if budget.category:
                tx_qs = tx_qs.filter(name__icontains=budget.category)

            spent = tx_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            remaining = budget.amount - spent
            progress = 0
            if budget.amount > 0:
                progress = min(100, int((spent / budget.amount) * 100))

            budget_items.append(
                {
                    'budget': budget,
                    'spent': spent,
                    'remaining': remaining,
                    'progress': progress,
                    'is_over': spent > budget.amount,
                    'is_warning': progress >= budget.alert_threshold,
                }
            )

        context['budget_items'] = budget_items
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class BudgetUpdateView(UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_edit.html'
    success_url = reverse_lazy('budgets')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


@method_decorator(login_required(login_url='login'), name='dispatch')
class BudgetDeleteView(DeleteView):
    model = Budget
    template_name = 'budgets/budget_confirm_delete.html'
    success_url = reverse_lazy('budgets')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)


@login_required(login_url='login')
def reports(request):
    account, _ = Account.objects.get_or_create(
        user=request.user,
        defaults={'name': f'{request.user.username} Main Account'}
    )

    today = date.today()
    selected_year = int(request.GET.get('year', today.year))
    selected_month = int(request.GET.get('month', today.month))

    start = date(selected_year, selected_month, 1)
    if selected_month == 12:
        end_exclusive = date(selected_year + 1, 1, 1)
    else:
        end_exclusive = date(selected_year, selected_month + 1, 1)

    month_tx = account.transactions.filter(due_date__gte=start, due_date__lt=end_exclusive)
    month_expenses = month_tx.expenses()
    month_incomes = month_tx.incomes()
    month_loans = month_tx.loans()

    total_expense = month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_income = month_incomes.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_loans = month_loans.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    net = total_income - (total_expense + total_loans)

    category_breakdown = (
        month_expenses.values('name')
        .annotate(total=Sum('amount'))
        .order_by('-total')[:6]
    )

    daily_expense = (
        month_expenses.annotate(day=TruncDay('due_date'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    expenses_by_month = list(
        account.transactions.expenses()
        .annotate(month=TruncMonth('due_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    incomes_by_month = list(
        account.transactions.incomes()
        .annotate(month=TruncMonth('due_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    expense_map = {row['month']: row['total'] for row in expenses_by_month}
    income_map = {row['month']: row['total'] for row in incomes_by_month}
    months = sorted(set(expense_map.keys()) | set(income_map.keys()))[-6:]
    trends = [
        {
            'month': month.strftime('%b %Y'),
            'expenses': expense_map.get(month, Decimal('0.00')),
            'income': income_map.get(month, Decimal('0.00')),
        }
        for month in months
    ]

    month_options = [(i, calendar.month_name[i]) for i in range(1, 13)]
    year_options = list(range(today.year - 3, today.year + 1))

    context = {
        'selected_year': selected_year,
        'selected_month': selected_month,
        'month_options': month_options,
        'year_options': year_options,
        'month_label': f"{calendar.month_name[selected_month]} {selected_year}",
        'total_expense': total_expense,
        'total_income': total_income,
        'total_loans': total_loans,
        'net': net,
        'category_breakdown': category_breakdown,
        'daily_expense': daily_expense,
        'trends': trends,
    }
    return render(request, 'fin_manager/reports.html', context)


def healthcheck(request):
    return HttpResponse('ok', content_type='text/plain')
