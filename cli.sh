#!/usr/bin/env bash
# CLI launcher for Link to QR: resolves the Python environment and runs cli.py.
# IMPORTANT: never `cd` here. Output files default to the caller's working directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"

if [ -n "${QR_CODE_PYTHON:-}" ] && [ -x "$QR_CODE_PYTHON" ]; then
    PYTHON_CMD="$QR_CODE_PYTHON"
elif [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
else
    echo "Creating virtual environment in $SCRIPT_DIR/.venv (first run)..." >&2
    python3 -m venv "$SCRIPT_DIR/.venv" >&2
    "$SCRIPT_DIR/.venv/bin/pip" install --quiet --disable-pip-version-check -r "$SCRIPT_DIR/requirements.txt" >&2
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
fi

exec "$PYTHON_CMD" "$SCRIPT_DIR/cli.py" "$@"
