#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def clean(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--pyside-wheel", required=True)
    parser.add_argument("--shiboken-wheel", required=True)
    parser.add_argument("--sdk", required=True)
    parser.add_argument("--ndk", required=True)
    args = parser.parse_args()

    project = Path(args.project).resolve()
    spec = project / "pysidedeploy.spec"
    content = f"""[app]
title = Daymark
project_dir = {clean(project)}
input_file = {clean(project / 'main.py')}
exec_directory = {clean(project / 'dist-android')}
project_file =
icon = {clean(project / 'icon.png')}

[python]
python_path = {clean(args.python)}
packages = Nuitka==4.1.1
android_packages = buildozer==1.5.0,cython==0.29.33

[qt]
qml_files =
excluded_qml_plugins =
modules = Core,Gui,Widgets
plugins =

[android]
wheel_pyside = {clean(args.pyside_wheel)}
wheel_shiboken = {clean(args.shiboken_wheel)}
plugins = platforms_qtforandroid

[nuitka]
macos.permissions =
mode = onefile
extra_args = --quiet --noinclude-qt-translations

[buildozer]
mode = debug
recipe_dir =
jars_dir =
ndk_path = {clean(args.ndk)}
sdk_path = {clean(args.sdk)}
local_libs =
arch = aarch64
"""
    spec.write_text(content, encoding="utf-8")
    print(f"Wrote {spec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
