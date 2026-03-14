# API Contract Status (Akaunti vs Current Django API)

This tracks alignment between `akaunti_reference/django_api/api_urls.py` and the live routes in `fin_manager/api_urls.py`.

## Implemented

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/verify/`
- `GET /api/auth/me/`
- `GET/PATCH /api/auth/profile/`
- `GET/POST /api/accounts/`
- `GET/PUT/DELETE /api/accounts/<id>/`
- `GET /api/categories/`
- `GET/POST /api/expenses/`
- `GET/PUT/DELETE /api/expenses/<id>/`
- `GET/POST /api/income/`
- `GET/PUT/DELETE /api/income/<id>/`
- `GET/POST /api/loans/` (project-specific extension)
- `GET/POST /api/budgets/`
- `GET/PUT/DELETE /api/budgets/<id>/`
- `GET /api/reports/monthly/`
- `GET /api/reports/trends/`
- `GET /api/dashboard/`
- `POST /api/sync/`
- `POST /api/receipts/`
- `POST /api/fcm/register/`
- `POST /api/sms/parse/`

## Partially Aligned

- `accounts/`
  - Akaunti reference uses UUID account ids.
  - Current app uses integer ids and a one-account-per-user model constraint.

## Not Yet Implemented

- None from the current target list.

## Flutter Base URL

Use `ApiConfig.apiBaseUrl` from [mobile/flutter_app/lib/core/config/api_config.dart](mobile/flutter_app/lib/core/config/api_config.dart).

### Build Examples

- Emulator (default):
  - `flutter run`
- Physical device on LAN:
  - `flutter run --dart-define=API_BASE_URL=http://<LAN-IP>:8000/api/`
- Release build:
  - `flutter build apk --release --dart-define=API_BASE_URL=https://<your-domain>/api/`
