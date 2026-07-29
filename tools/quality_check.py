#!/usr/bin/env python3
"""Dependency-free repository checks suitable for local use and CI."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {'.git', '.venv', '.buildozer', 'dist-android', 'android-wheels', 'deployment'}
FORBIDDEN_SUFFIXES = {'.apk', '.aab', '.jks', '.keystore', '.sqlite', '.sqlite3', '.db', '.log'}
SECRET_PATTERNS = {
    'private key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'GitHub token': re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{30,}\b'),
}
LINK_PATTERN = re.compile(r'(?<!!)[(]([^()]+)[)]|!\[[^]]*]\(([^()]+)\)')


def files() -> list[Path]:
    return [
        path for path in ROOT.rglob('*')
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
    ]


def check_python(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if path.suffix != '.py':
            continue
        try:
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f'Python parse failed: {path.relative_to(ROOT)}: {exc}')
    return errors


def check_forbidden_artifacts(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f'Forbidden tracked artifact: {path.relative_to(ROOT)}')
    return errors


def check_secrets(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        if path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.zip'}:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f'Possible {name}: {path.relative_to(ROOT)}')
    return errors


def check_plantuml(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        if path.suffix != '.puml':
            continue
        text = path.read_text(encoding='utf-8').strip()
        if not text.startswith('@startuml') or not text.endswith('@enduml'):
            errors.append(f'Invalid PlantUML wrapper: {path.relative_to(ROOT)}')
    return errors


def check_markdown_links(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        if path.suffix.lower() != '.md':
            continue
        text = path.read_text(encoding='utf-8')
        # Support both ordinary and image Markdown links.
        candidates = re.findall(r'!?\[[^]]*]\(([^)]+)\)', text)
        for raw in candidates:
            target = raw.strip().split()[0].strip('<>')
            if not target or target.startswith(('#', 'http://', 'https://', 'mailto:')):
                continue
            target = target.split('#', 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f'Broken relative link in {path.relative_to(ROOT)}: {target}')
        # HTML image links used by GitHub README files.
        for target in re.findall(r'<img[^>]+src=["\']([^"\']+)', text):
            if target.startswith(('http://', 'https://')):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f'Broken HTML image in {path.relative_to(ROOT)}: {target}')
    return errors


def main() -> int:
    paths = files()
    errors: list[str] = []
    errors += check_python(paths)
    errors += check_forbidden_artifacts(paths)
    errors += check_secrets(paths)
    errors += check_plantuml(paths)
    errors += check_markdown_links(paths)

    if errors:
        print('Quality checks failed:')
        for error in errors:
            print(f'  - {error}')
        return 1

    print(f'Quality checks passed for {len(paths)} tracked files.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
