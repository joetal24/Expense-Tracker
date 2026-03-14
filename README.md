# Finance Manager

A from-scratch Django finance tracker focused on clean architecture and deployment-ready defaults.

## What was rebuilt

- Replaced mixed legacy model design with a clear domain:
  - `Account` (one account per user)
  - `Transaction` (typed records: `expense` or `loan`)
- Introduced a service layer in `fin_manager/services.py` for dashboard period summaries.
- Refactored forms/views around the new domain model.
- Simplified routing and standardized health check at `/healthz/`.
- Updated admin configuration for operational visibility.

## Core Architecture

- **Domain layer**: `fin_manager/models.py`
- **Application/service layer**: `fin_manager/services.py`
- **Presentation layer**: `fin_manager/views.py` + templates
- **Interface/API layer**: `fin_manager/urls.py`
- **Ops/config layer**: `FinanceManager/settings.py`, Leapcell deployment docs

## Features

- User registration and authentication
- Dashboard totals by weekly / monthly / yearly windows
- Expense capture and list (grouped by month)
- Loan capture and list (with interest rate)
- Admin management for accounts and transactions
- Health endpoint for platform probes

## Tech Stack

- Python 3.12+
- Django 4.2
- Gunicorn
- SQLite (local) or Postgres via `DATABASE_URL`

## Local Setup

1. Create and activate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Run the app:

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Routes

- `/` dashboard/home
- `/expenses/` expense list + create
- `/loans/` loan list + create
- `/accounts/login/` login
- `/accounts/register/` registration
- `/healthz/` health probe
- `/admin/` Django admin

## Deployment Notes

- Supports `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, and `DATABASE_URL`.
- For container environments, use Gunicorn with `/tmp` worker temp dir as documented in `LEAPCELL_DEPLOY.md`.
- For production release execution, follow `APK_LEAPCELL_GO_LIVE_CHECKLIST.md`.
