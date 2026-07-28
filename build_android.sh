#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
printf 'Daymark Android builder v7 (persistent cache + OpenSSL 403 guard)\n'

fail() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }
info() { printf '\n==> %s\n' "$*"; }

[[ "$(uname -s)" == "Darwin" ]] || fail "This build script is intended for macOS."
[[ "$ROOT" != *" "* ]] || fail "Move the project to a path without spaces: $ROOT"
[[ -f "$ROOT/main.py" ]] || fail "main.py is missing."
[[ -f "$ROOT/icon.png" ]] || fail "Place your launcher icon at $ROOT/icon.png and rerun."

if command -v sips >/dev/null 2>&1; then
    WIDTH="$(sips -g pixelWidth "$ROOT/icon.png" 2>/dev/null | awk '/pixelWidth/ {print $2}')"
    HEIGHT="$(sips -g pixelHeight "$ROOT/icon.png" 2>/dev/null | awk '/pixelHeight/ {print $2}')"
    [[ -n "$WIDTH" && -n "$HEIGHT" ]] || fail "icon.png is not a readable PNG."
    [[ "$WIDTH" == "$HEIGHT" ]] || fail "icon.png must be square; found ${WIDTH}x${HEIGHT}."
    if (( WIDTH < 512 )); then
        fail "icon.png should be at least 512x512; found ${WIDTH}x${HEIGHT}."
    fi
    info "Using icon.png (${WIDTH}x${HEIGHT})"
fi

find_python311() {
    if command -v python3.11 >/dev/null 2>&1; then command -v python3.11; return; fi
    if command -v brew >/dev/null 2>&1; then
        local p
        p="$(brew --prefix python@3.11 2>/dev/null || true)"
        [[ -x "$p/bin/python3.11" ]] && { echo "$p/bin/python3.11"; return; }
    fi
    return 1
}

PY311="$(find_python311 || true)"
[[ -n "$PY311" ]] || fail "Python 3.11 is required. Run ./setup_android_toolchain.sh first."
"$PY311" - <<'PY' || fail "The selected interpreter is not Python 3.11."
import sys
assert sys.version_info[:2] == (3, 11), sys.version
PY

jdk_major() {
    local home="$1"
    [[ -x "$home/bin/java" ]] || return 1
    "$home/bin/java" -version 2>&1 | sed -n '1s/.*version "\([0-9][0-9]*\).*/\1/p'
}

find_jdk17() {
    local candidate major prefix
    if command -v brew >/dev/null 2>&1; then
        prefix="$(brew --prefix openjdk@17 2>/dev/null || true)"
        candidate="$prefix/libexec/openjdk.jdk/Contents/Home"
        major="$(jdk_major "$candidate" || true)"
        [[ "$major" == "17" ]] && { echo "$candidate"; return; }
    fi
    candidate="$(/usr/libexec/java_home -v 17 2>/dev/null || true)"
    major="$(jdk_major "$candidate" || true)"
    [[ "$major" == "17" ]] && { echo "$candidate"; return; }
    return 1
}

JAVA_HOME_17="$(find_jdk17 || true)"
[[ -n "$JAVA_HOME_17" ]] || fail "A real JDK 17 installation was not found. Run: brew install openjdk@17"
export JAVA_HOME="$JAVA_HOME_17"
export PATH="$JAVA_HOME/bin:$PATH"
hash -r
[[ "$(jdk_major "$JAVA_HOME")" == "17" ]] || fail "Selected JAVA_HOME is not JDK 17: $JAVA_HOME"
info "Using JDK 17 from $JAVA_HOME"
"$JAVA_HOME/bin/java" -version

VENV="${DAYMARK_ANDROID_VENV:-$ROOT/../.daymark-android-venv}"
if [[ -d "$VENV" ]] && [[ ! -x "$VENV/bin/python" ]]; then
    rm -rf "$VENV"
fi
if [[ ! -d "$VENV" ]]; then
    info "Creating the Android build environment outside the project"
    "$PY311" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# Re-assert Java after virtual-environment activation and immediately before
# every Android deployment command so other shell settings cannot override JDK 17.
export JAVA_HOME="$JAVA_HOME_17"
export PATH="$JAVA_HOME/bin:$PATH"
hash -r
JAVA_MAJOR="$(java -version 2>&1 | sed -n '1s/.*version "\([0-9][0-9]*\).*/\1/p')"
[[ "$JAVA_MAJOR" == "17" ]] || fail "JDK 17 was selected but java reports major version ${JAVA_MAJOR:-unknown}."

info "Installing the pinned host deployment tools"
python -m pip install --upgrade pip
python -m pip install --upgrade -r "$ROOT/requirements-android-host.txt"
python "$ROOT/tools/patch_android_deploy.py"

WHEEL_DIR="${DAYMARK_ANDROID_WHEELS:-$ROOT/android-wheels}"
mkdir -p "$WHEEL_DIR"
PYSIDE_NAME="pyside6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl"
SHIBOKEN_NAME="shiboken6-6.11.1-6.11.1-cp311-cp311-android_aarch64.whl"
PYSIDE_WHEEL="$WHEEL_DIR/$PYSIDE_NAME"
SHIBOKEN_WHEEL="$WHEEL_DIR/$SHIBOKEN_NAME"

find_existing_wheel() {
    local pattern="$1"
    find "$WHEEL_DIR" "$HOME/Downloads" "$HOME/.pyside6_android_deploy" \
        -maxdepth 5 -type f -iname "$pattern" 2>/dev/null | head -n 1 || true
}

if [[ ! -f "$PYSIDE_WHEEL" ]]; then
    FOUND="$(find_existing_wheel '*pyside6*6.11.1*cp311*android*aarch64*.whl')"
    if [[ -n "$FOUND" ]]; then cp "$FOUND" "$PYSIDE_WHEEL"; fi
fi
if [[ ! -f "$SHIBOKEN_WHEEL" ]]; then
    FOUND="$(find_existing_wheel '*shiboken6*6.11.1*cp311*android*aarch64*.whl')"
    if [[ -n "$FOUND" ]]; then cp "$FOUND" "$SHIBOKEN_WHEEL"; fi
fi

if [[ ! -f "$PYSIDE_WHEEL" ]]; then
    info "Downloading the official PySide6 6.11.1 Android ARM64 wheel"
    curl -fL --retry 3 -o "$PYSIDE_WHEEL" \
      "https://download.qt.io/official_releases/QtForPython/pyside6/$PYSIDE_NAME"
fi
if [[ ! -f "$SHIBOKEN_WHEEL" ]]; then
    info "Downloading the official Shiboken6 6.11.1 Android ARM64 wheel"
    curl -fL --retry 3 -o "$SHIBOKEN_WHEEL" \
      "https://download.qt.io/official_releases/QtForPython/shiboken6/$SHIBOKEN_NAME"
fi

python - "$PYSIDE_WHEEL" "$SHIBOKEN_WHEEL" <<'PY'
from pathlib import Path
import sys, zipfile
for raw in sys.argv[1:]:
    p = Path(raw)
    if not zipfile.is_zipfile(p):
        raise SystemExit(f"Invalid wheel: {p}")
    lower = p.name.lower()
    if "cp311" not in lower or "android_aarch64" not in lower or "6.11.1" not in lower:
        raise SystemExit(f"Wrong Android wheel: {p.name}")
print("Android wheels validated.")
PY

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
[[ -n "$SDK" ]] || fail "Android SDK not found. Run ./setup_android_toolchain.sh first."

find_sdkmanager() {
    for candidate in \
        "$SDK/cmdline-tools/latest/bin/sdkmanager" \
        "$SDK/cmdline-tools/bin/sdkmanager" \
        "$SDK/tools/bin/sdkmanager"; do
        [[ -x "$candidate" ]] && { echo "$candidate"; return; }
    done
    if command -v sdkmanager >/dev/null 2>&1; then command -v sdkmanager; return; fi
    if command -v brew >/dev/null 2>&1; then
        local brew_prefix
        brew_prefix="$(brew --prefix 2>/dev/null || true)"
        [[ -x "$brew_prefix/share/android-commandlinetools/cmdline-tools/latest/bin/sdkmanager" ]] && \
          { echo "$brew_prefix/share/android-commandlinetools/cmdline-tools/latest/bin/sdkmanager"; return; }
    fi
    return 1
}
SDKMANAGER="$(find_sdkmanager || true)"

sdk_components_ready() {
    [[ -x "$SDK/platform-tools/adb" ]] &&
    [[ -f "$SDK/platforms/android-36/android.jar" ]] &&
    [[ -x "$SDK/build-tools/36.0.0/aapt2" ]] &&
    [[ -x "$SDK/build-tools/36.0.0/aidl" ]] &&
    [[ -x "$SDK/build-tools/36.0.0/zipalign" ]]
}

if sdk_components_ready; then
    info "Android platform-tools, API 36, and build tools 36.0.0 are already installed"
else
    [[ -n "$SDKMANAGER" ]] || fail       "Required Android SDK packages are missing and sdkmanager was not found."

    info "Installing missing Android SDK packages"
    yes | "$SDKMANAGER" --sdk_root="$SDK" --licenses >/dev/null 2>&1 || true

    if ! "$SDKMANAGER" --sdk_root="$SDK" --verbose \
      "platform-tools" "platforms;android-36" "build-tools;36.0.0"; then
        cat >&2 <<EOF

ERROR: sdkmanager could not fetch Google's package manifests.
This is a network/proxy/DNS/TLS problem, not a PySide6 problem.

Test the repository with:
  curl -I --connect-timeout 20 https://dl.google.com/android/repository/repository2-1.xml

SDK selected by this build:
  $SDK

Required local files:
  $SDK/platform-tools/adb
  $SDK/platforms/android-36/android.jar
  $SDK/build-tools/36.0.0/aapt2
  $SDK/build-tools/36.0.0/zipalign
EOF
        exit 1
    fi
fi

sdk_components_ready || fail   "Android SDK installation is incomplete: platform-tools, android-36, or build-tools 36.0.0 is missing."

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
if [[ -z "$NDK" && -n "$SDKMANAGER" ]]; then
    info "Installing Android NDK 27.2.12479018"
    "$SDKMANAGER" --sdk_root="$SDK" "ndk;27.2.12479018"
    NDK="$SDK/ndk/27.2.12479018"
fi
[[ -n "$NDK" && -f "$NDK/source.properties" ]] || fail "NDK 27.2.12479018 was not found."
grep -q 'Pkg.Revision = 27.2.12479018' "$NDK/source.properties" || \
  fail "Wrong NDK version at $NDK. Expected 27.2.12479018."

export ANDROID_SDK_ROOT="$SDK"
export ANDROID_HOME="$SDK"
export ANDROID_NDK_HOME="$NDK"
export PATH="$SDK/platform-tools:$PATH"

python "$ROOT/tools/write_pysidedeploy_spec.py" \
  --project "$ROOT" \
  --python "$VENV/bin/python" \
  --pyside-wheel "$PYSIDE_WHEEL" \
  --shiboken-wheel "$SHIBOKEN_WHEEL" \
  --sdk "$SDK" \
  --ndk "$NDK"

mkdir -p "$ROOT/dist-android"
rm -f "$ROOT/dist-android/build.log" "$ROOT/dist-android/Daymark-debug-arm64-v8a.apk"
find "$ROOT/bin" -maxdepth 1 -type f -name '*.apk' -delete 2>/dev/null || true

if [[ "${DAYMARK_CLEAN_BUILD:-0}" == "1" ]]; then
    info "Performing requested clean Android build"
    rm -rf "$ROOT/.buildozer" "$ROOT/buildozer.spec" "$ROOT/deployment"
else
    info "Preserving the Android compiler cache for a faster, more reliable incremental build"
    # Deployment recipes and specs are regenerated from current source, while
    # expensive CPython/OpenSSL/Qt compiler outputs remain cached.
    rm -rf "$ROOT/buildozer.spec" "$ROOT/deployment"
fi

# python-for-android currently points the OpenSSL 3.3.1 recipe at openssl.org,
# which may return HTTP 403. Preseed the exact archive and marker from the
# official GitHub release so p4a can continue without hitting that URL.
OPENSSL_VERSION="3.3.1"
OPENSSL_PACKAGE_DIR="$ROOT/.buildozer/android/platform/build-arm64-v8a/packages/openssl"
OPENSSL_ARCHIVE="$OPENSSL_PACKAGE_DIR/openssl-${OPENSSL_VERSION}.tar.gz"
OPENSSL_MARKER="$OPENSSL_PACKAGE_DIR/.mark-openssl-${OPENSSL_VERSION}.tar.gz"
mkdir -p "$OPENSSL_PACKAGE_DIR"
if [[ -s "$OPENSSL_ARCHIVE" ]] && ! tar -tzf "$OPENSSL_ARCHIVE" >/dev/null 2>&1; then
    info "Removing an invalid cached OpenSSL archive"
    rm -f "$OPENSSL_ARCHIVE" "$OPENSSL_MARKER"
fi
if [[ ! -s "$OPENSSL_ARCHIVE" ]]; then
    info "Downloading OpenSSL ${OPENSSL_VERSION} from the official GitHub release"
    curl -fL --retry 5 --retry-delay 2 --retry-all-errors \
      -A "Mozilla/5.0" \
      -o "$OPENSSL_ARCHIVE" \
      "https://github.com/openssl/openssl/releases/download/openssl-${OPENSSL_VERSION}/openssl-${OPENSSL_VERSION}.tar.gz"
fi
tar -tzf "$OPENSSL_ARCHIVE" >/dev/null 2>&1 || \
  fail "The cached OpenSSL archive is invalid: $OPENSSL_ARCHIVE"
touch "$OPENSSL_MARKER"
info "OpenSSL source cache prepared at $OPENSSL_ARCHIVE"

info "Building Daymark debug APK for arm64-v8a"
set +e
env JAVA_HOME="$JAVA_HOME_17" PATH="$JAVA_HOME_17/bin:$PATH" \
  DAYMARK_OFFLINE_ANDROID_SDK=1 \
  DAYMARK_PRESERVE_BUILDOZER=1 \
  pyside6-android-deploy \
  --config-file "$ROOT/pysidedeploy.spec" \
  --ndk-path "$NDK" \
  --sdk-path "$SDK" \
  --wheel-pyside "$PYSIDE_WHEEL" \
  --wheel-shiboken "$SHIBOKEN_WHEEL" \
  --keep-deployment-files \
  -f -v 2>&1 | tee "$ROOT/dist-android/build.log"
STATUS=${PIPESTATUS[0]}
set -e
if (( STATUS != 0 )); then
    printf '\nBuild failed. The complete log is at:\n  %s\n' "$ROOT/dist-android/build.log" >&2
    printf 'Run ./capture_android_log.sh only after an APK installs and crashes on launch.\n' >&2
    exit "$STATUS"
fi

python "$ROOT/tools/verify_apk.py" --project "$ROOT"
info "APK ready: $ROOT/dist-android/Daymark-debug-arm64-v8a.apk"
