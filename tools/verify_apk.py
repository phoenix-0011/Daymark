#!/usr/bin/env python3
"""Verify the APK without rejecting python-for-android's libpythonbin.so."""
from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

VERIFIER_VERSION = "Daymark APK verifier v4"


def newest_apk(paths: list[Path]) -> Path | None:
    files: list[Path] = []
    for root in paths:
        if root.exists():
            files.extend(root.rglob("*.apk"))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--apk")
    args = parser.parse_args()
    print(VERIFIER_VERSION)
    project = Path(args.project).resolve()
    apk = Path(args.apk).resolve() if args.apk else newest_apk(
        [project / "dist-android", project / "bin", project]
    )
    if apk is None or not apk.is_file():
        raise SystemExit("No APK was produced.")
    with zipfile.ZipFile(apk) as archive:
        names = set(archive.namelist())
    required = {
        "lib/arm64-v8a/libpython3.11.so",
        "lib/arm64-v8a/libshiboken6.abi3.so",
        "lib/arm64-v8a/libpyside6.abi3.so",
    }
    missing = sorted(required - names)
    incompatible = []
    for name in sorted(names):
        if not name.startswith("lib/arm64-v8a/libpython"):
            continue
        base = Path(name).name
        if base == "libpythonbin.so":
            continue
        match = re.fullmatch(r"libpython(\d+)\.(\d+)(?:[a-z]*)\.so", base)
        if match and match.groups() != ("3", "11"):
            incompatible.append(name)
    if missing:
        raise SystemExit("APK verification failed; missing: " + ", ".join(missing))
    if incompatible:
        raise SystemExit(
            "APK verification failed; incompatible versioned Python runtime: "
            + ", ".join(incompatible)
        )
    buildozer_spec = project / "buildozer.spec"
    if buildozer_spec.exists():
        spec = buildozer_spec.read_text(encoding="utf-8", errors="replace")
        for pin in ("python3==3.11.15", "hostpython3==3.11.15"):
            if pin not in spec:
                raise SystemExit(f"Generated buildozer.spec is missing {pin}.")
        if "--load-local-libs=python3.11" in spec or "python3.11,plugins_platforms" in spec:
            raise SystemExit("Generated buildozer.spec incorrectly loads python3.11 as a Qt local library.")
    output_dir = project / "dist-android"
    output_dir.mkdir(parents=True, exist_ok=True)
    final_apk = output_dir / "Daymark-debug-arm64-v8a.apk"
    if apk != final_apk:
        shutil.copy2(apk, final_apk)
    print(f"Verified APK: {final_apk}")
    print("  CPython: 3.11")
    print("  python-for-android launcher: libpythonbin.so allowed")
    print("  ABI: arm64-v8a")
    print("  PySide6/Shiboken6: present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
