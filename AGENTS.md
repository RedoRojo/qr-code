# Agent Guide — Link to QR (`tools qr`)

Fast reference for AI agents invoking or maintaining `qr-code`.

## 1. Invoking from an Agent

- **Never start the web server (`./run.sh`)** to generate QR codes. Always invoke the CLI (`tools qr` or `./cli.sh`).
- **Pass `--json -q`** for structured JSON output on `stdout` and silent progress on `stderr`.
- **Exit codes**: `0` = success, `1` = runtime error, `2` = usage error.

### Common Recipes

```bash
# 1. Generate PNG in current directory (auto-named qr-<slug>.png, never overwrites)
tools qr "https://example.com" --json -q

# 2. Generate PNG or SVG at an explicit path with custom size & hex colors
tools qr "https://example.com" -o /tmp/code.svg --size 512 --fg "#1e3a8a" --bg "#ffffff" --error H --json -q

# 3. Print compact Unicode QR directly in the terminal
tools qr "https://example.com" --terminal -q

# 4. Read content from stdin
printf "Wi-Fi credentials" | tools qr - -o wifi.png --json -q
```

### JSON Output Schema (`--json`)

```json
{
  "content": "https://example.com",
  "format": "png",
  "size": 370,
  "version": 2,
  "error": "H",
  "modules": 25,
  "output": "/abs/path/to/qr-example-com.png",
  "bytes": 462
}
```

## 2. Codebase Map

- `core/qr.py`: Pure-Python QR rendering via `segno` (`render_qr`, `save_qr`, `terminal_qr`, `validate_color`, `slugify`).
- `cli.py` / `cli.sh`: CLI adapter (`argparse`). Never `cd` inside `cli.sh`.
- `app.py` / `static/index.html`: Lightweight stdlib HTTP server + browser UI.
- `tests/test_cli.py` & `tests/test_app.py`: Test suite (`./.venv/bin/python -m unittest discover -s tests -v`).
