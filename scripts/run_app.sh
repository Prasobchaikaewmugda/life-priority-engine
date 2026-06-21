#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
APP_PATH="$PROJECT_ROOT/app.py"

if [[ ! -f "$APP_PATH" ]]; then
    echo "Streamlit entry point not found: $APP_PATH" >&2
    exit 1
fi

if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="$(command -v python)"
else
    echo "Python was not found. Create .venv or add Python to PATH." >&2
    exit 1
fi

echo "Starting Life Priority Engine from $PROJECT_ROOT"
exec "$PYTHON_CMD" -m streamlit run "$APP_PATH"
