#!/usr/bin/env python3
"""
Link to QR - Lightweight HTTP Server
Simple tool to convert URLs and text into QR codes.
Uses only the Python 3 standard library.
"""

import mimetypes
import os
import signal
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = (BASE_DIR / "static").resolve()
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 8003))


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class QRRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format, *args):
        sys.stdout.write(f"[Link-to-QR] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

    def do_HEAD(self):
        self._handle_request(send_body=False)

    def do_GET(self):
        self._handle_request(send_body=True)

    def _handle_request(self, send_body: bool = True):
        url_path = self.path.split("?", 1)[0]

        # Root page
        if url_path in ("", "/", "/index.html"):
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8", send_body)
            return

        # Health check endpoint
        if url_path == "/health":
            payload = b'{"status":"ok","tool":"qr-code"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            if send_body:
                self.wfile.write(payload)
            return

        # Serve static assets (e.g. /qrcode.min.js or /static/...)
        clean_path = url_path.lstrip("/")
        if clean_path.startswith("static/"):
            clean_path = clean_path[len("static/"):]

        if not clean_path:
            self.send_error(404, "Resource not found")
            return

        try:
            target_file = (STATIC_DIR / clean_path).resolve()
        except OSError:
            self.send_error(404, "Resource not found")
            return

        if not target_file.is_relative_to(STATIC_DIR) or not target_file.is_file():
            self.send_error(404, "Resource not found")
            return

        mime_type, _ = mimetypes.guess_type(str(target_file))
        if target_file.suffix.lower() == ".js":
            mime_type = "application/javascript; charset=utf-8"
        self._serve_file(target_file, mime_type or "application/octet-stream", send_body)

    def _serve_file(self, file_path: Path, content_type: str, send_body: bool = True):
        try:
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if send_body:
                self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Failed to serve file: {e}")


def create_server(host: str = HOST, port: int = PORT) -> ReusableThreadingHTTPServer:
    return ReusableThreadingHTTPServer((host, port), QRRequestHandler)


def run():
    def handle_shutdown(sig, frame):
        print("\n[Link-to-QR] Shutting down server...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        httpd = create_server(HOST, PORT)
    except OSError as e:
        print(f"[ERROR] Could not bind to {HOST}:{PORT}: {e}", file=sys.stderr)
        sys.exit(1)

    print("==========================================================")
    print(" Link to QR started successfully")
    print(f" Server available at: http://{HOST}:{PORT}")
    print("==========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Link-to-QR] Shutting down server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run()
