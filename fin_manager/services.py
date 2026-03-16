from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Transaction


def build_period_ranges(today=None):
    current_day = today or timezone.localdate()

    week_start = current_day - timedelta(days=current_day.weekday())
    week_end = week_start + timedelta(days=6)

    month_start = current_day.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)

    year_start = current_day.replace(month=1, day=1)
    year_end = current_day.replace(month=12, day=31)

    return {
        'weekly': (week_start, week_end),
        'monthly': (month_start, month_end),
        'yearly': (year_start, year_end),
    }


def build_dashboard_summary(account):
    periods = build_period_ranges()
    transactions = Transaction.objects.filter(account=account)

    totals = {}
    period_labels = {}

    for key, (start_date, end_date) in periods.items():
        in_period = transactions.in_period(start_date, end_date)
        expenses = in_period.expenses().total_amount()
        loans = in_period.loans().total_amount()
        incomes = in_period.incomes().total_amount()
        combined = in_period.total_amount() if in_period.exists() else Decimal('0.00')
        net_savings = incomes - expenses - loans
        totals[key] = {
            'expenses': expenses,
            'loans': loans,
            'incomes': incomes,
            'combined': combined,
            'net_savings': net_savings,
        }
        period_labels[key] = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

    # Budget progress (monthly)
    monthly_budget = account.monthly_budget or Decimal('0.00')
    monthly_expenses = totals['monthly']['expenses']
    budget_progress = (monthly_expenses / monthly_budget * 100) if monthly_budget > 0 else None

    # Savings target progress
    savings_target = account.savings_target or Decimal('0.00')
    monthly_net_savings = totals['monthly']['net_savings']
    savings_progress = (monthly_net_savings / savings_target * 100) if savings_target > 0 else None

    return {
        'totals': totals,
        'periods': period_labels,
        'budget_progress': float(budget_progress) if budget_progress is not None else None,
        'monthly_budget': monthly_budget,
        'savings_progress': float(savings_progress) if savings_progress is not None else None,
        'savings_target': savings_target,
    }
