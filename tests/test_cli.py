"""
CLI tests for Link to QR. Standard library only (unittest + subprocess).
Requires `segno` (installed in .venv by cli.sh). Run with:
    .venv/bin/python -m unittest discover -s tests -v
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CLI = BASE_DIR / "cli.py"
sys.path.insert(0, str(BASE_DIR))

try:
    import segno  # noqa: F401
    HAS_SEGNO = True
except ImportError:
    HAS_SEGNO = False


def run_cli(*args, cwd=None, stdin=None, text=True):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=text, cwd=cwd, input=stdin, timeout=60,
    )


class CoreHelperTests(unittest.TestCase):
    def test_validate_color(self):
        from core.qr import validate_color

        self.assertEqual(validate_color("#FFF"), "#ffffff")
        self.assertEqual(validate_color("1e3a8a"), "#1e3a8a")
        with self.assertRaises(ValueError):
            validate_color("blue-ish")

    def test_slugify(self):
        from core.qr import slugify

        self.assertEqual(slugify("https://www.example.com/a?b=c"), "example-com-a-b-c")
        self.assertEqual(slugify("!!!"), "code")


class CLIUsageTests(unittest.TestCase):
    def test_help_exits_zero(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)

    def test_missing_content_is_usage_error(self):
        self.assertEqual(run_cli().returncode, 2)

    def test_invalid_error_level_is_usage_error(self):
        self.assertEqual(run_cli("x", "--error", "Z").returncode, 2)


@unittest.skipUnless(HAS_SEGNO, "segno not installed in this interpreter")
class CLIGenerationTests(unittest.TestCase):
    def test_png_default_name_in_cwd_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = run_cli("https://example.com", cwd=tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            out = Path(first.stdout.strip())
            self.assertEqual(out, Path(tmp).resolve() / "qr-example-com.png")
            self.assertTrue(out.read_bytes().startswith(b"\x89PNG"))

            second = run_cli("https://example.com", cwd=tmp)
            self.assertEqual(Path(second.stdout.strip()).name, "qr-example-com-1.png")

    def test_svg_from_extension_with_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "code.svg"
            result = run_cli("hello", "-o", str(target), "--size", "512", "--fg", "#1e3a8a", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["format"], "svg")
            self.assertEqual(payload["output"], str(target.resolve()))
            self.assertLessEqual(payload["size"], 512)
            self.assertIn("<svg", target.read_text(encoding="utf-8"))
            self.assertIn("#1e3a8a", target.read_text(encoding="utf-8"))

    def test_stdin_and_terminal(self):
        result = run_cli("-", "--terminal", stdin="piped text\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(len(result.stdout.splitlines()), 5)

    def test_raw_bytes_to_stdout(self):
        result = run_cli("hello", "-o", "-", text=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith(b"\x89PNG"))

    def test_invalid_color_is_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("hello", "--fg", "nope", cwd=tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
