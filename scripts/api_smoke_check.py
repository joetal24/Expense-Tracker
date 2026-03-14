import json
import os
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinanceManager.settings')

import django


django.setup()

from django.core.management import call_command
from rest_framework.test import APIClient


def main() -> int:
    call_command('migrate', interactive=False, verbosity=0)

    client = APIClient()

    username = f"smoke_{uuid.uuid4().hex[:8]}"
    password = "SmokePass123!"

    steps = []

    def expect(status_code: int, expected: int, name: str, payload=None):
        ok = status_code == expected
        steps.append({
            'step': name,
            'ok': ok,
            'expected': expected,
            'received': status_code,
            'payload': payload,
        })
        return ok

    register_response = client.post(
        '/api/auth/register/',
        {'username': username, 'password': password},
        format='json',
    )
    expect(register_response.status_code, 201, 'register')

    login_response = client.post(
        '/api/auth/login/',
        {'username': username, 'password': password},
        format='json',
    )
    if not expect(login_response.status_code, 200, 'login'):
        print(json.dumps({'ok': False, 'steps': steps}, indent=2, default=str))
        return 1

    access = login_response.json().get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    me_response = client.get('/api/auth/me/')
    expect(me_response.status_code, 200, 'me')

    expense_response = client.post(
        '/api/expenses/',
        {
            'name': 'Smoke Transport',
            'amount': '15000',
            'due_date': '2026-03-14',
            'notes': 'Taxi',
        },
        format='json',
    )
    expect(expense_response.status_code, 201, 'create-expense')

    income_response = client.post(
        '/api/income/',
        {
            'name': 'Smoke Income',
            'amount': '90000',
            'due_date': '2026-03-14',
            'notes': 'Freelance',
        },
        format='json',
    )
    expect(income_response.status_code, 201, 'create-income')

    dashboard_response = client.get('/api/dashboard/')
    expect(dashboard_response.status_code, 200, 'dashboard')

    report_response = client.get('/api/reports/monthly/?year=2026&month=3')
    expect(report_response.status_code, 200, 'report-monthly')

    sms_response = client.post(
        '/api/sms/parse/',
        {'sms': 'You have sent UGX 15,000 to John Doe. Transaction ID: MTN20260313.'},
        format='json',
    )
    expect(sms_response.status_code, 200, 'sms-parse')

    sync_response = client.post(
        '/api/sync/',
        {
            'expenses': [
                {
                    'name': 'Smoke Market',
                    'amount': '45000',
                    'due_date': '2026-03-15',
                    'notes': 'Groceries',
                }
            ],
            'incomes': [
                {
                    'name': 'Smoke Side Hustle',
                    'amount': '120000',
                    'due_date': '2026-03-16',
                    'notes': 'Delivery work',
                }
            ],
        },
        format='json',
    )
    expect(sync_response.status_code, 200, 'sync')

    all_ok = all(step['ok'] for step in steps)
    print(json.dumps({'ok': all_ok, 'steps': steps}, indent=2, default=str))
    return 0 if all_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
