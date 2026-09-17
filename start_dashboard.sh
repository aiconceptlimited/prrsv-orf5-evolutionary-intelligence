#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [ ! -x "$PROJECT_ROOT/venv/bin/python" ]; then
    echo "ERROR: project virtual environment not found at $PROJECT_ROOT/venv"
    exit 1
fi

exec "$PROJECT_ROOT/venv/bin/python" "$PROJECT_ROOT/dashboard_complete.py"
