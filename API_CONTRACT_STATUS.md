# API Contract Status (Akaunti vs Current Django API)

This tracks alignment between `akaunti_reference/django_api/api_urls.py` and the live routes in `fin_manager/api_urls.py`.

## Implemented

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`
- `GET/PUT /api/accounts/` (singleton account endpoint)
- `GET /api/categories/`
- `GET/POST /api/expenses/`
- `GET/POST /api/income/`
- `GET/POST /api/loans/` (project-specific extension)
- `GET /api/reports/monthly/`
- `GET /api/reports/trends/`
- `GET /api/dashboard/`
- `POST /api/sync/`
- `POST /api/receipts/`
- `POST /api/fcm/register/`
- `POST /api/sms/parse/`

## Partially Aligned

- `accounts/`
  - Akaunti reference uses list/create + detail by UUID.
  - Current app uses a single account resource at `/api/accounts/` for authenticated user.

## Not Yet Implemented

- `POST /api/auth/verify/`
- `PATCH /api/auth/profile/`
- `GET/PUT/DELETE /api/accounts/<id>/`
- `GET/PUT/DELETE /api/expenses/<id>/`
- `GET/PUT/DELETE /api/income/<id>/`
- `GET/POST /api/budgets/`
- `GET/PUT/DELETE /api/budgets/<id>/`

## Flutter Base URL

Use `ApiConfig.apiBaseUrl` from [mobile/flutter_app/lib/core/config/api_config.dart](mobile/flutter_app/lib/core/config/api_config.dart).

### Build Examples

- Emulator (default):
  - `flutter run`
- Physical device on LAN:
  - `flutter run --dart-define=API_BASE_URL=http://<LAN-IP>:8000/api/`
- Release build:
  - `flutter build apk --release --dart-define=API_BASE_URL=https://<your-domain>/api/`
