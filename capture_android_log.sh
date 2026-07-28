#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$ROOT/dist-android/daymark-logcat.txt}"
SDK="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-$HOME/.pyside6_android_deploy/android-sdk}}"
ADB="${ADB:-$SDK/platform-tools/adb}"
[[ -x "$ADB" ]] || ADB="$(command -v adb || true)"
[[ -x "$ADB" ]] || { echo "adb not found." >&2; exit 1; }
"$ADB" logcat -d -v threadtime | grep -Ei \
  'daymark|python|pyside|shiboken|qt|FATAL EXCEPTION|AndroidRuntime|linker|dlopen|UnsatisfiedLinkError' \
  > "$OUT" || true
echo "Saved filtered log to: $OUT"
