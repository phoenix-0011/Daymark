#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APK="${1:-$ROOT/dist-android/Daymark-debug-arm64-v8a.apk}"
[[ -f "$APK" ]] || { echo "APK not found: $APK" >&2; exit 1; }

find_sdk() {
  for d in "${ANDROID_SDK_ROOT:-}" "${ANDROID_HOME:-}" "$HOME/.pyside6_android_deploy/android-sdk" "$HOME/Library/Android/sdk"; do
    [[ -n "$d" && -d "$d" ]] && { echo "$d"; return; }
  done
}
SDK="$(find_sdk || true)"
ADB="${ADB:-${SDK:+$SDK/platform-tools/adb}}"
[[ -x "$ADB" ]] || ADB="$(command -v adb || true)"
[[ -x "$ADB" ]] || { echo "adb not found." >&2; exit 1; }

"$ADB" start-server
DEVICES="$("$ADB" devices | awk 'NR>1 && $2=="device" {print $1}')"
[[ -n "$DEVICES" ]] || {
  "$ADB" devices
  echo "No authorized Android device. Unlock the phone and accept the USB debugging prompt." >&2
  exit 1
}

"$ADB" install -r "$APK"

AAPT=""
if [[ -n "$SDK" ]]; then
  AAPT="$(find "$SDK/build-tools" -type f -name aapt 2>/dev/null | sort | tail -n 1)"
fi
PACKAGE=""
if [[ -x "$AAPT" ]]; then
  PACKAGE="$("$AAPT" dump badging "$APK" | sed -n "s/package: name='\([^']*\)'.*/\1/p" | head -n 1)"
fi
if [[ -n "$PACKAGE" ]]; then
  echo "Launching $PACKAGE"
  "$ADB" shell monkey -p "$PACKAGE" -c android.intent.category.LAUNCHER 1 >/dev/null
else
  echo "Installed. Open Daymark from the phone launcher."
fi
