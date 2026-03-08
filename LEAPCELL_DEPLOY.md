# Leapcell Deployment Guide

This project can be deployed on Leapcell using only UI commands (no interactive shell needed).

## 1) Service Settings

- **Framework Preset:** Django
- **Runtime:** Python 3.11 (or any supported 3.x runtime)
- **Root Directory:** `./`
- **Serving Port:** `8080`

## 2) Build Command

Use this exact command:

```bash
python -m pip install --upgrade pip && if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install Django==4.2.4 gunicorn; fi && python manage.py migrate && python manage.py collectstatic --noinput
```

Why this works:
- avoids `uv pip` virtualenv errors in container builds,
- installs dependencies from `requirements.txt` when present,
- still works if `requirements.txt` is missing,
- runs migrations and static collection during image build.

## 3) Start Command

```bash
gunicorn --bind 0.0.0.0:8080 --worker-tmp-dir /tmp --pid /tmp/gunicorn.pid --access-logfile - --error-logfile - FinanceManager.wsgi:application
```

## 4) Environment Variables

Set these in Leapcell:

- `DJANGO_SECRET_KEY` = a generated secret
- `DJANGO_DEBUG` = `False`
- `DJANGO_ALLOWED_HOSTS` = `*` (quick start) or your exact Leapcell domain
- `DATABASE_URL` = your managed Postgres connection string
- `TMPDIR` = `/tmp`

Notes:
- `DATABASE_URL` is recommended on Leapcell because SQLite can fail on read-only runtimes.
- Keep `DATABASE_SSL_REQUIRE=True` (default in this project) for managed cloud Postgres unless your provider says otherwise.

Generate a secret key locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 5) Common Failure Fixes

### `error: No virtual environment found` from `uv pip`
Use the Build Command above (pip-based), not `uv pip`.

### `STATIC_ROOT setting` error
Already fixed in this project with:

```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### `DisallowedHost`
Set `DJANGO_ALLOWED_HOSTS` in Leapcell to your deployed domain (or `*` temporarily).

### `Read-only file system`
Use the Start Command above (with `--worker-tmp-dir /tmp` and `--pid /tmp/gunicorn.pid`) and set `TMPDIR=/tmp`.
