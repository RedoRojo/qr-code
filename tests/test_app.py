"""
Unit and HTTP integration tests for Link to QR.
Uses only the Python 3 standard library.
"""

import http.client
import json
import sys
import threading
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_server


class LinkToQRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def _request(self, method: str, path: str):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request(method, path)
            res = conn.getresponse()
            body = res.read()
            return res.status, dict(res.getheaders()), body
        finally:
            conn.close()

    def test_root_html_is_english_and_accessible(self):
        status, headers, body = self._request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        html = body.decode("utf-8")

        self.assertIn('<html lang="en">', html)
        self.assertIn('<meta name="color-scheme" content="light dark">', html)
        self.assertIn("Instant QR Code Generator", html)
        self.assertIn("Copy Image to Clipboard", html)
        self.assertIn("Download PNG", html)
        self.assertIn("Download SVG", html)

        # Accessibility & modern web compliance checks
        self.assertNotIn("onclick=", html)
        self.assertIn('role="status"', html)
        self.assertIn('role="alert"', html)

        # Ensure no leftover Spanish UI copy
        for spanish_term in ("Generador", "Herramienta", "Pegar", "Descargar", "Portapapeles", "Limpiar"):
            self.assertNotIn(spanish_term, html)

    def test_head_requests_return_headers_without_body(self):
        for path in ("/", "/health", "/qrcode.min.js"):
            status, _, body = self._request("HEAD", path)
            self.assertEqual(status, 200)
            self.assertEqual(body, b"")

    def test_health_endpoint(self):
        status, headers, body = self._request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers.get("Content-Type", ""))
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data, {"status": "ok", "tool": "qr-code"})

    def test_static_js_served(self):
        for path in ("/qrcode.min.js", "/static/qrcode.min.js"):
            status, headers, body = self._request("GET", path)
            self.assertEqual(status, 200)
            self.assertIn("javascript", headers.get("Content-Type", ""))
            self.assertIn(b"QRCode", body)

    def test_path_traversal_blocked(self):
        for path in ("/../app.py", "/static/../app.py", "/../../etc/passwd"):
            status, _, _ = self._request("GET", path)
            self.assertEqual(status, 404)

    def test_missing_route_returns_404(self):
        status, _, _ = self._request("GET", "/does-not-exist")
        self.assertEqual(status, 404)

    def test_tool_json_metadata_in_english(self):
        tool_json = BASE_DIR / "tool.json"
        data = json.loads(tool_json.read_text(encoding="utf-8"))
        self.assertEqual(data["id"], "qr-code")
        self.assertEqual(data["name"], "Link to QR")
        self.assertEqual(data["category"], "Utilities")
        self.assertEqual(data["port"], 8003)
        self.assertIn("QR code", data["description"])


if __name__ == "__main__":
    unittest.main()
