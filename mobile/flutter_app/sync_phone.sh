#!/usr/bin/env bash
set -euo pipefail

DEVICE_ID="${1:-dfffe2fb}"
API_BASE_URL="${API_BASE_URL:-https://xpense-racker-joetal246596-vck4udhn.leapcell.dev/api/}"
APP_ID="com.example.ugandan_finance_app"

echo "[1/4] Checking device connection..."
adb devices -l | grep -q "${DEVICE_ID}.*device" || {
  echo "Device ${DEVICE_ID} not found/authorized."
  echo "Run: adb devices -l"
  exit 1
}

echo "[2/4] Building debug APK..."
flutter build apk --debug --dart-define=API_BASE_URL="${API_BASE_URL}"

echo "[3/4] Installing APK on ${DEVICE_ID}..."
adb -s "${DEVICE_ID}" install -r build/app/outputs/flutter-apk/app-debug.apk

echo "[4/4] Launching app..."
adb -s "${DEVICE_ID}" shell monkey -p "${APP_ID}" -c android.intent.category.LAUNCHER 1 >/dev/null

echo "Done. App updated on phone."
