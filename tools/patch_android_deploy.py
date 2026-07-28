#!/usr/bin/env python3
"""Pin CPython 3.11 and make Buildozer use the installed Android SDK offline."""
from __future__ import annotations

import site
from pathlib import Path

EXPECTED_PYSIDE = "6.11.1"
OLD = 'python3,shiboken6,PySide6'
NEW = 'python3==3.11.15,hostpython3==3.11.15,shiboken6,PySide6'
ARCH_LINE = '        self.set_value("app", "android.archs", pysidedeploy_config.arch)'
API_BLOCK = (
    ARCH_LINE
    + '\n        self.set_value("app", "android.api", "36")'
    + '\n        self.set_value("app", "android.minapi", "28")'
    + '\n        self.set_value("app", "android.skip_update", "True")'
)
OFFLINE_MARKER = "DAYMARK_OFFLINE_ANDROID_SDK"
PRESERVE_MARKER = "DAYMARK_PRESERVE_BUILDOZER"
CLEANUP_CONTEXT = '        buildozer_build: Path = config.project_dir / ".buildozer"\n'
CLEANUP_OLD = CLEANUP_CONTEXT + '        if buildozer_build.exists():'
CLEANUP_NEW = (
    CLEANUP_CONTEXT
    + '        if (buildozer_build.exists()\n'
    + '                and os.environ.get("DAYMARK_PRESERVE_BUILDOZER") != "1"):'
)
FUNCTION_HEADER = "    def _install_android_packages(self):\n"
OFFLINE_GUARD = """        # Daymark: use the already-installed SDK without network updates.
        if os.environ.get("DAYMARK_OFFLINE_ANDROID_SDK") == "1":
            required = [
                join(self.android_sdk_dir, "platform-tools", "adb"),
                join(self.android_sdk_dir, "platforms", f"android-{self.android_api}", "android.jar"),
                join(self.android_sdk_dir, "build-tools", "36.0.0", "aapt2"),
                join(self.android_sdk_dir, "build-tools", "36.0.0", "aidl"),
                join(self.android_sdk_dir, "build-tools", "36.0.0", "zipalign"),
            ]
            missing = [path for path in required if not os.path.exists(path)]
            if missing:
                raise BuildozerException(
                    "Daymark offline SDK check failed; missing: " + ", ".join(missing)
                )
            self.buildozer.info(
                "Using preinstalled Android SDK components; skipping sdkmanager network/update checks"
            )
            return True
"""


def site_roots() -> list[Path]:
    roots = [Path(p) for p in site.getsitepackages()]
    user_site = site.getusersitepackages()
    if user_site:
        roots.append(Path(user_site))
    return roots


def patch_pyside() -> tuple[list[Path], list[Path]]:
    candidates: list[Path] = []
    for root in site_roots():
        if root.exists():
            candidates.extend(root.rglob("buildozer.py"))
    patched: list[Path] = []
    already: list[Path] = []
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "class BuildozerConfig" not in text or "p4a.bootstrap" not in text:
            continue
        requirements_ready = NEW in text
        api_ready = 'self.set_value("app", "android.api", "36")' in text
        skip_ready = 'self.set_value("app", "android.skip_update", "True")' in text
        if requirements_ready and api_ready and skip_ready:
            already.append(path)
            continue
        if not requirements_ready and OLD not in text:
            continue
        if (not api_ready or not skip_ready) and ARCH_LINE not in text:
            continue
        backup = path.with_suffix(path.suffix + ".daymark-backup")
        if not backup.exists():
            backup.write_text(text, encoding="utf-8")
        if not requirements_ready:
            text = text.replace(OLD, NEW, 1)
        if not api_ready or not skip_ready:
            older = (
                ARCH_LINE
                + '\n        self.set_value("app", "android.api", "36")'
                + '\n        self.set_value("app", "android.minapi", "28")'
            )
            if older in text:
                text = text.replace(older, API_BLOCK, 1)
            else:
                text = text.replace(ARCH_LINE, API_BLOCK, 1)
        path.write_text(text, encoding="utf-8")
        patched.append(path)
    return patched, already


def patch_buildozer_target() -> tuple[list[Path], list[Path]]:
    candidates: list[Path] = []
    for root in site_roots():
        path = root / "buildozer" / "targets" / "android.py"
        if path.exists():
            candidates.append(path)
    patched: list[Path] = []
    already: list[Path] = []
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        if OFFLINE_MARKER in text:
            already.append(path)
            continue
        if FUNCTION_HEADER not in text:
            continue
        backup = path.with_suffix(path.suffix + ".daymark-backup")
        if not backup.exists():
            backup.write_text(text, encoding="utf-8")
        text = text.replace(FUNCTION_HEADER, FUNCTION_HEADER + OFFLINE_GUARD, 1)
        path.write_text(text, encoding="utf-8")
        patched.append(path)
    return patched, already


def patch_pyside_cleanup() -> tuple[list[Path], list[Path]]:
    """Keep .buildozer when Daymark asks for an incremental Android build.

    PySide's Android deploy cleanup normally deletes the entire project-local
    .buildozer directory. That also deletes the pre-seeded OpenSSL source archive
    before python-for-android can use it, causing openssl.org HTTP 403 failures.
    """
    candidates: list[Path] = []
    for root in site_roots():
        if root.exists():
            candidates.extend(root.rglob("deploy_util.py"))
    patched: list[Path] = []
    already: list[Path] = []
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "def cleanup(" not in text or 'buildozer_build: Path = config.project_dir / ".buildozer"' not in text:
            continue
        if PRESERVE_MARKER in text:
            already.append(path)
            continue
        if CLEANUP_OLD not in text:
            continue
        backup = path.with_suffix(path.suffix + ".daymark-backup")
        if not backup.exists():
            backup.write_text(text, encoding="utf-8")
        if "import os\n" not in text:
            if "import logging\n" in text:
                text = text.replace("import logging\n", "import logging\nimport os\n", 1)
            else:
                text = "import os\n" + text
        text = text.replace(CLEANUP_OLD, CLEANUP_NEW, 1)
        path.write_text(text, encoding="utf-8")
        patched.append(path)
    return patched, already


def main() -> int:
    try:
        import PySide6
    except ImportError as exc:
        raise SystemExit(f"PySide6 is not installed in this build environment: {exc}")
    if PySide6.__version__ != EXPECTED_PYSIDE:
        raise SystemExit(
            f"Expected PySide6 {EXPECTED_PYSIDE}, found {PySide6.__version__}. "
            "Delete the Android build virtual environment and rerun build_android.sh."
        )
    pyside_patched, pyside_already = patch_pyside()
    target_patched, target_already = patch_buildozer_target()
    cleanup_patched, cleanup_already = patch_pyside_cleanup()
    if not pyside_patched and not pyside_already:
        raise SystemExit("Could not find the PySide6 Android Buildozer configuration to patch.")
    if not target_patched and not target_already:
        raise SystemExit("Could not find buildozer/targets/android.py for the offline SDK fix.")
    if not cleanup_patched and not cleanup_already:
        raise SystemExit("Could not patch PySide6 Android cleanup to preserve .buildozer.")
    for path in pyside_patched:
        print(f"Pinned Python 3.11.15, API 36/min API 28, and skip_update in: {path}")
    for path in pyside_already:
        print(f"PySide Android deployment patch already present in: {path}")
    for path in target_patched:
        print(f"Applied offline Android SDK validation patch in: {path}")
    for path in target_already:
        print(f"Offline Android SDK patch already present in: {path}")
    for path in cleanup_patched:
        print(f"Applied persistent .buildozer cache patch in: {path}")
    for path in cleanup_already:
        print(f"Persistent .buildozer cache patch already present in: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
