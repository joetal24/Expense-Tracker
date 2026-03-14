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
        totals[key] = {
            'expenses': in_period.expenses().total_amount(),
            'loans': in_period.loans().total_amount(),
            'combined': in_period.total_amount() if in_period.exists() else Decimal('0.00'),
        }
        period_labels[key] = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

    return {
        'totals': totals,
        'periods': period_labels,
    }
