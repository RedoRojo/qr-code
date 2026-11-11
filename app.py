#!/usr/bin/env python3
"""
Link to QR - Servidor HTTP Ligero
Herramienta sencilla para convertir enlaces y texto a códigos QR.
Usa únicamente la biblioteca estándar de Python 3.
"""

import os
import sys
import mimetypes
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
PORT = int(os.environ.get("PORT", 8003))

class QRRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format, *args):
        sys.stdout.write(f"[Link-to-QR] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

    def do_GET(self):
        url_path = self.path.split("?")[0]

        # Health check y raíz
        if url_path in ["", "/", "/index.html"]:
            self.serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        elif url_path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","tool":"qr-code"}')
            return

        # Servir estáticos directos (por ej. /qrcode.min.js o /static/...)
        clean_path = url_path.lstrip("/")
        if clean_path.startswith("static/"):
            clean_path = clean_path[len("static/"):]

        target_file = STATIC_DIR / clean_path
        if target_file.is_file():
            mime_type, _ = mimetypes.guess_type(str(target_file))
            self.serve_file(target_file, mime_type or "application/octet-stream")
            return

        self.send_error(404, "Recurso no encontrado")

    def serve_file(self, file_path: Path, content_type: str):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error al servir archivo: {e}")

def run():
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, QRRequestHandler)
    print("==========================================================")
    print(" Link to QR iniciado exitosamente")
    print(f" Servidor disponible en: http://127.0.0.1:{PORT}")
    print("==========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run()
