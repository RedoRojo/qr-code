# Link to QR ⚡

Fast, lightweight, and clean tool to convert any URL or text into a high-resolution QR code, from the browser **or** the command line.

## ✨ Features

- ⚡ **Live Generation**: The QR code updates instantaneously as you type or paste your link.
- 📋 **Copy to Clipboard**: Copy the QR PNG image in a single click to paste directly into chats or documents.
- 📥 **Multi-Format Download**:
  - **PNG** (High resolution, ideal for presentations or sharing).
  - **SVG** (Pure scalable vector graphics with zero quality loss).
- 🔗 **Link Preview**: Quick button to open and verify the target URL in a new tab.
- 🎨 **Instant Customization**: Adjust size, error correction level, foreground color, and background color.
- 🌗 **Adaptive Theme**: Supports light and dark themes following your system preference with an optional manual toggle.
- ⌨️ **CLI**: Generate PNG/SVG files, pipe content from stdin, or print the QR code straight into your terminal.
- 🚀 **Lightweight**: The web server uses only Python's standard library; the CLI adds a single pure-Python dependency (`segno`).

## 🌐 Web Interface

```bash
./run.sh
```

The server will start on `http://127.0.0.1:8003` (configurable via `$HOST` and `$PORT`), or launch it from **Tools Hub**.

## ⌨️ Command Line Interface

Via the global Tools Hub dispatcher (recommended):

```bash
tools qr "https://example.com"                         # -> ./qr-example-com.png
tools qr "https://example.com" -o code.svg --size 512  # SVG, 512 px
tools qr "Wi-Fi password" --fg "#1e3a8a" --error M     # custom color and error level
echo "https://example.com" | tools qr - --terminal     # read stdin, print in terminal
tools qr "hello" -o - > hello.png                      # raw bytes to stdout
tools qr "hello" --json                                # machine-readable result
```

Or standalone from this repository: `./cli.sh "https://example.com"`.

| Option | Default | Description |
| :--- | :--- | :--- |
| `-o, --output` | `qr-<slug>.<format>` in the current dir | Output file or directory (`-` = stdout). Never overwrites without `-o`. |
| `-f, --format` | from `-o` extension, else `png` | `png` or `svg` |
| `-s, --size` | `384` | Target size in pixels |
| `-e, --error` | `H` | Error correction level: `L`, `M`, `Q`, `H` |
| `--fg` / `--bg` | `#000000` / `#ffffff` | Foreground and background colors |
| `--border` | `4` | Quiet zone in modules |
| `-t, --terminal` | – | Print the QR code in the terminal instead of saving |
| `--json`, `-q`, `-v` | – | JSON output, quiet mode, verbose errors |

The first run of `cli.sh` creates a local `.venv` and installs `requirements.txt` automatically.

## 🧪 Running Tests

```bash
.venv/bin/python -m unittest discover -s tests -v   # full suite (web + CLI)
python3 -m unittest discover -s tests -v            # web suite; CLI generation tests skip without segno
```
