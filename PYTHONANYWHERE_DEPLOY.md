# PythonAnywhere Deployment (JoeTal)

This guide deploys this Django project to `JoeTal.pythonanywhere.com`.

## 1) Push latest code to GitHub

From your local machine:

```bash
git add .
git commit -m "Prepare for PythonAnywhere deployment"
git push origin main
```

## 2) Create PythonAnywhere web app

1. Log in to PythonAnywhere.
2. Go to **Web** → **Add a new web app**.
3. Choose **Manual configuration**.
4. Choose Python `3.10` (or the closest available version).

## 3) Create virtual environment + install dependencies

Open a **Bash console** on PythonAnywhere and run:

```bash
mkvirtualenv --python=/usr/bin/python3.10 expensetracker-env
workon expensetracker-env
cd /home/JoeTal
git clone https://github.com/predystopic-dev/Finance-Manager.git Expense-Tracker
cd /home/JoeTal/Expense-Tracker
pip install -r requirements.txt
```

## 4) Set environment variables (Bash console)

Add to your `~/.bashrc`:

```bash
echo 'export DJANGO_SECRET_KEY="replace_with_a_long_random_secret"' >> ~/.bashrc
echo 'export DJANGO_DEBUG="False"' >> ~/.bashrc
echo 'export DJANGO_ALLOWED_HOSTS="JoeTal.pythonanywhere.com"' >> ~/.bashrc
source ~/.bashrc
workon expensetracker-env
```

## 5) Run migrations + collect static

```bash
cd /home/JoeTal/Expense-Tracker
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 6) Configure WSGI file

Go to **Web** tab → open your WSGI config file and replace with:

```python
import os
import sys

path = '/home/JoeTal/Expense-Tracker'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinanceManager.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 7) Configure static files mapping (Web tab)

- URL: `/static/`
- Directory: `/home/JoeTal/Expense-Tracker/staticfiles`

Then click **Reload**.

## 8) Update after future code changes

In PythonAnywhere Bash console:

```bash
workon expensetracker-env
cd /home/JoeTal/Expense-Tracker
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** in the Web tab.
