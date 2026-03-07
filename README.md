# Finance Manager

A simple personal finance tracker built with Django.

## Features

- User registration and login/logout
- Home dashboard
- Expense/liability entry form
- Expense list grouped by month
- Admin panel for data management

## Tech Stack

- Python
- Django
- HTML/CSS
- JavaScript
- SQLite (default Django database)

## Prerequisites

- Python 3.10+ (recommended)
- `uv`

## Installation

1. Clone the repository and enter the project folder:

	```bash
	git clone https://github.com/predystopic-dev/Finance-Manager.git
	cd Finance-Manager
	```

2. Create and activate a virtual environment:

	```bash
	uv venv .venv
	source .venv/bin/activate
	```

3. Install dependencies:

	```bash
	uv pip install -r requirements.txt
	```

4. Apply migrations:

	```bash
	python manage.py migrate
	```

5. (Optional) Create an admin user:

	```bash
	python manage.py createsuperuser
	```

6. Run the development server:

	```bash
	python manage.py runserver
	```

7. Open the app in your browser:

	```
	http://127.0.0.1:8000/
	```

## Routes

- `/` - Home
- `/expenses/` - Expense page
- `/accounts/login/` - Login
- `/accounts/register/` - Register
- `/admin/` - Django admin

## Notes

- The project uses SQLite by default (`db.sqlite3`).
- Authentication routes are provided by `django.contrib.auth.urls`.

## Repository

- GitHub: https://github.com/predystopic-dev/Finance-Manager
