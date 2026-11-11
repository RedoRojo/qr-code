#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-8003}"
export PORT

echo "Starting Link to QR at http://127.0.0.1:$PORT ..."
exec python3 app.py
