# Akaunti APK Quickstart (Applied to this Repo)

This repo now contains the Akaunti source assets for fast mobile delivery:

- Flutter app scaffold: [mobile/flutter_app](mobile/flutter_app)
- Django API reference: [akaunti_reference/django_api](akaunti_reference/django_api)
- Architecture doc source: `Akaunti_UG_Technical_Architecture.docx`

## 1) Architecture Mapping (from Akaunti technical doc)

Akaunti uses an **offline-first 3-tier approach**:

1. Flutter Android app (local-first storage, sync queue)
2. Django REST API (JWT auth + sync/report endpoints)
3. PostgreSQL backend

Your current project already has the finance domain (`Account`, `Transaction`) in `fin_manager`.
Use that as the source of truth while adding REST APIs for mobile.

## 2) What was bootstrapped now

- Extracted original Akaunti Flutter source into `mobile/flutter_app`.
- Extracted original Akaunti Django API reference into `akaunti_reference/django_api`.

This gives you a ready mobile base + API contract examples to speed up implementation.

## 3) Immediate next backend upgrades (recommended)

To connect the Flutter app to this Django project, add:

- `djangorestframework`
- `djangorestframework-simplejwt`
- `django-cors-headers`

Then create API routes under `/api/` in this project, starting with:

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET/POST /api/accounts/`
- `GET/POST /api/expenses/`
- `GET /api/dashboard/`
- `POST /api/sync/` (optional phase 2)

Reference endpoint style in: `akaunti_reference/django_api/api_urls.py`

### Status update

The current backend now includes:

- auth: register/login/refresh/me
- accounts/categories
- expenses/income/loans
- reports (monthly/trends) + dashboard
- sync
- receipts upload
- fcm registration
- sms parse

Track detailed parity in: [API_CONTRACT_STATUS.md](API_CONTRACT_STATUS.md)

## 4) Flutter run/build steps

From repo root:

```bash
cd mobile/flutter_app
flutter pub get
flutter run
```

Release APK:

```bash
flutter build apk --release
```

APK output:

`mobile/flutter_app/build/app/outputs/flutter-apk/app-release.apk`

## 5) Environment wiring for Flutter

Set your API base URL in the app service layer (e.g. `lib/core/services/*`) to your Django host.

Local example:

- Android emulator to host machine: `http://10.0.2.2:8000/api/`
- Physical device on same network: `http://<your-lan-ip>:8000/api/`

## 6) Suggested phased delivery

Phase 1 (fastest APK):
- auth + account + expenses + dashboard read endpoints
- Flutter login, dashboard, add expense, transaction list

Phase 2:
- SMS parsing endpoint + on-device parser integration
- offline sync queue endpoint (`/api/sync/`)
- budgets/reports/notifications

## 7) Deployment target from Akaunti doc

Use your existing deployment path (`LEAPCELL_DEPLOY.md`) and expose `/api/*` + `/healthz/`.

For production mobile use, move to PostgreSQL and keep JWT + HTTPS only.
