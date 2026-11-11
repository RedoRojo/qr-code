# Link to QR ⚡

Fast, lightweight, and clean web tool to convert any URL or text into a high-resolution QR code.

## ✨ Features

- ⚡ **Live Generation**: The QR code updates instantaneously as you type or paste your link.
- 📋 **Copy to Clipboard**: Copy the QR PNG image in a single click to paste directly into chats or documents.
- 📥 **Multi-Format Download**:
  - **PNG** (High resolution, ideal for presentations or sharing).
  - **SVG** (Pure scalable vector graphics with zero quality loss).
- 🔗 **Link Preview**: Quick button to open and verify the target URL in a new tab.
- 🎨 **Instant Customization**: Adjust size, error correction level, foreground color, and background color.
- 🌗 **Adaptive Theme**: Supports light and dark themes following your system preference with an optional manual toggle.
- 🚀 **Zero Heavy Dependencies**: Runs 100% offline using Python's standard library.

## 🚀 Standalone Usage

```bash
./run.sh
```

The server will start on `http://127.0.0.1:8003` (configurable via `$HOST` and `$PORT`).

## 🧪 Running Tests

```bash
python3 -m unittest discover -s tests -v
```
