#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m compileall -q main.py daymark tests tools
python tools/quality_check.py
python -m pytest -q
python -m coverage erase
python -m coverage run -m pytest -q
python -m coverage report -m

if python -m ruff --version >/dev/null 2>&1; then
  python -m ruff check main.py daymark tests tools
else
  printf 'NOTE: Ruff is not installed; install requirements-dev.txt for linting.\n'
fi

printf 'All available local checks completed.\n'
