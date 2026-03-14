# APK + Leapcell Go-Live Checklist

Use this as a strict release runbook.

## 0) Preconditions

- Backend code is on `main` and pushed.
- Flutter SDK is installed on your build machine.
- Android SDK/build-tools are installed.
- You have a Leapcell project and DB connection string.

---

## 1) Backend deploy on Leapcell

### 1.1 Configure service

- Framework: `Django`
- Runtime: Python 3.x
- Port: `8080`

### 1.2 Build command

```bash
python -m pip install --upgrade pip && if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install Django==4.2.4 gunicorn; fi && python manage.py migrate && python manage.py collectstatic --noinput
```

### 1.3 Start command

```bash
gunicorn --bind 0.0.0.0:8080 --worker-tmp-dir /tmp --pid /tmp/gunicorn.pid --access-logfile - --error-logfile - FinanceManager.wsgi:application
```

### 1.4 Environment variables

- `DJANGO_SECRET_KEY=<generated-secret>`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=<your-leapcell-domain>`
- `DATABASE_URL=<postgres-url>`
- `TMPDIR=/tmp`

---

## 2) Backend smoke verification (production URL)

Set:

```bash
BASE="https://<your-leapcell-domain>"
```

### 2.1 Health check

```bash
curl -i "$BASE/healthz/"
```

Expect: `200` + `ok`.

### 2.2 Auth + JWT

```bash
curl -s -X POST "$BASE/api/auth/register/" -H 'Content-Type: application/json' -d '{"username":"release_user","password":"StrongPass123!"}'
TOKEN=$(curl -s -X POST "$BASE/api/auth/login/" -H 'Content-Type: application/json' -d '{"username":"release_user","password":"StrongPass123!"}' | python -c "import sys,json; print(json.load(sys.stdin)['access'])")
```

### 2.3 Core API checks

```bash
curl -s "$BASE/api/auth/me/" -H "Authorization: Bearer $TOKEN"
curl -s "$BASE/api/categories/" -H "Authorization: Bearer $TOKEN"
curl -s -X POST "$BASE/api/expenses/" -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"name":"Release Expense","amount":"15000","due_date":"2026-03-14","notes":"smoke"}'
curl -s "$BASE/api/dashboard/" -H "Authorization: Bearer $TOKEN"
```

### 2.4 Extended API checks

```bash
curl -s -X POST "$BASE/api/income/" -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"name":"Release Income","amount":"100000","due_date":"2026-03-14","notes":"smoke"}'
curl -s -X POST "$BASE/api/loans/" -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"name":"Release Loan","amount":"250000","interest_rate":"4.5","due_date":"2026-06-01","notes":"smoke"}'
curl -s "$BASE/api/reports/monthly/?year=2026&month=3" -H "Authorization: Bearer $TOKEN"
curl -s "$BASE/api/reports/trends/" -H "Authorization: Bearer $TOKEN"
curl -s -X POST "$BASE/api/sms/parse/" -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" -d '{"sms":"You have sent UGX 15,000 to John Doe. Transaction ID: MTN20260313."}'
```

---

## 3) Flutter app wiring

Use API config file:

- `mobile/flutter_app/lib/core/config/api_config.dart`

Build with production API URL:

```bash
cd mobile/flutter_app
flutter create .
flutter pub get
flutter run --dart-define=API_BASE_URL=https://<your-leapcell-domain>/api/
```

If `flutter run` passes, create release APK:

```bash
flutter build apk --release --dart-define=API_BASE_URL=https://<your-leapcell-domain>/api/
```

APK output:

- `mobile/flutter_app/build/app/outputs/flutter-apk/app-release.apk`

---

## 4) Device UAT (must pass)

- Login works.
- Create expense works.
- Create income works.
- Dashboard totals update.
- Reports endpoints load data.
- SMS parse trigger returns parsed result.
- Sync endpoint accepts batched payload.

---

## 5) Launch criteria

Launch only if all are true:

- Leapcell `/healthz/` returns `200`.
- All API smoke checks return success payloads.
- Flutter release APK builds successfully.
- Manual device UAT passes all items in section 4.
