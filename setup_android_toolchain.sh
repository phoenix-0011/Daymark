#!/usr/bin/env bash
set -Eeuo pipefail

fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }
info() { printf '\n==> %s\n' "$*"; }

[[ "$(uname -s)" == "Darwin" ]] || fail "This script is intended for macOS."
command -v brew >/dev/null 2>&1 || fail "Homebrew is required."

info "Installing/updating the host build dependencies"
brew install python@3.11 openjdk@21 cmake ninja autoconf automake libtool pkgconf

find_sdk() {
    for candidate in \
        "${ANDROID_SDK_ROOT:-}" \
        "${ANDROID_HOME:-}" \
        "$HOME/.pyside6_android_deploy/android-sdk" \
        "$HOME/.pyside6-android-deploy/android-sdk" \
        "$HOME/Library/Android/sdk"; do
        [[ -n "$candidate" && -d "$candidate" ]] && { echo "$candidate"; return; }
    done
    return 1
}

SDK="$(find_sdk || true)"
[[ -n "$SDK" ]] || fail "Android SDK was not found. Restore or install it before building."

for file in \
    "$SDK/platform-tools/adb" \
    "$SDK/platforms/android-36/android.jar" \
    "$SDK/build-tools/36.0.0/aapt2" \
    "$SDK/build-tools/36.0.0/zipalign"; do
    [[ -e "$file" ]] || fail "Required Android SDK component is missing: $file"
done

find_ndk() {
    for candidate in \
        "${ANDROID_NDK_HOME:-}" \
        "${ANDROID_NDK_ROOT:-}" \
        "$SDK/ndk/27.2.12479018" \
        "$HOME/.pyside6_android_deploy/android-ndk/AndroidNDK12479018.app/Contents/NDK" \
        "$HOME/.pyside6-android-deploy/android-ndk/AndroidNDK12479018.app/Contents/NDK"; do
        [[ -n "$candidate" && -f "$candidate/source.properties" ]] && { echo "$candidate"; return; }
    done
    return 1
}

NDK="$(find_ndk || true)"
[[ -n "$NDK" ]] || fail "Android NDK 27.2.12479018 was not found."
grep -q 'Pkg.Revision = 27.2.12479018' "$NDK/source.properties" || \
    fail "Wrong NDK version at $NDK. Expected 27.2.12479018."

JAVA_HOME_21="$(/usr/libexec/java_home -v 21 2>/dev/null || true)"
if [[ -z "$JAVA_HOME_21" ]]; then
    JAVA_HOME_21="$(brew --prefix openjdk@21)/libexec/openjdk.jdk/Contents/Home"
fi

printf '\nAndroid build environment is ready.\n'
printf 'SDK: %s\n' "$SDK"
printf 'NDK: %s\n' "$NDK"
printf 'JDK: %s\n' "$JAVA_HOME_21"
printf '\nRun ./build_android.sh\n'
