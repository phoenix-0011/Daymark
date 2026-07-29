#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v plantuml >/dev/null 2>&1 || { echo "PlantUML is not installed." >&2; exit 1; }
plantuml -charset UTF-8 -tsvg "$ROOT"/diagrams/*.puml
echo "SVG diagrams generated in docs/diagrams."
