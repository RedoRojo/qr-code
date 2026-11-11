#!/usr/bin/env python3
"""
Link to QR - Command Line Interface.

Thin adapter over core/qr.py: generates QR codes as PNG/SVG files or prints
them directly in the terminal. It never imports the web server (app.py).

Examples:
    tools qr "https://example.com"
    tools qr "https://example.com" -o code.svg --size 512 --fg "#1e3a8a"
    echo "some text" | tools qr - --terminal
"""

import argparse
import json
import os
import sys
from pathlib import Path

__version__ = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))  # make core/ importable from any working directory

PROG = os.environ.get("TOOLS_PROG", "cli.sh")
EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_INTERRUPTED = 0, 1, 2, 130


class CLIError(Exception):
    """Expected runtime error: printed without a traceback, exits with code 1."""


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def log(args, message: str) -> None:
    if not getattr(args, "quiet", False):
        print(message, file=sys.stderr, flush=True)


def emit(args, payload: dict, human: str) -> None:
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif human:
        print(human)


def resolve_output(requested, default_name: str) -> Path:
    """Explicit -o is used as-is (dirs get default_name); otherwise write to cwd without overwriting."""
    if requested:
        path = Path(requested).expanduser()
        if path.is_dir():
            path = path / default_name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path.resolve()

    path = Path.cwd() / default_name
    stem, suffix, counter = path.stem, path.suffix, 1
    while path.exists():
        path = path.with_name(f"{stem}-{counter}{suffix}")
        counter += 1
    return path.resolve()


def read_content(value: str) -> str:
    """Return QR content, reading from stdin when value is '-'."""
    if value == "-":
        if sys.stdin.isatty():
            raise CLIError("expected content on stdin (pipe text in or pass it as an argument).")
        value = sys.stdin.read()
    content = value.strip()
    if not content:
        raise CLIError("QR content cannot be empty.")
    return content


# ---------------------------------------------------------------------------
# Command handler
# ---------------------------------------------------------------------------

def cmd_generate(args) -> int:
    from core import qr

    content = read_content(args.content)
    options = dict(size=args.size, error=args.error, fg=args.fg, bg=args.bg, border=args.border)

    try:
        if args.terminal:
            art = qr.terminal_qr(content, error=args.error)
            emit(args, {"content": content, "terminal": art}, art.rstrip("\n"))
            return EXIT_OK

        # Write raw bytes to stdout: tools qr "text" -o - > code.png
        if args.output == "-":
            result = qr.render_qr(content, fmt=args.format or "png", **options)
            sys.stdout.buffer.write(result["data"])
            sys.stdout.buffer.flush()
            return EXIT_OK

        fmt = args.format
        if not fmt and args.output and Path(args.output).suffix.lower() in (".png", ".svg"):
            fmt = Path(args.output).suffix.lower().lstrip(".")
        fmt = fmt or "png"

        output = resolve_output(args.output, f"qr-{qr.slugify(content)}.{fmt}")
        result = qr.save_qr(content, output, fmt=fmt, **options)
    except ValueError as e:
        raise CLIError(str(e))

    payload = {"content": content, **result}
    human = result["output"]
    log(args, f"QR {result['format'].upper()} {result['size']}x{result['size']} px "
              f"(version {result['version']}, error {result['error']}) saved:")
    emit(args, payload, human)
    return EXIT_OK


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    from core.qr import DEFAULT_BG, DEFAULT_BORDER, DEFAULT_ERROR, DEFAULT_FG, DEFAULT_SIZE, ERROR_LEVELS, FORMATS

    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Generate a QR code from a link or text (PNG, SVG, or terminal output).",
        epilog=(
            "examples:\n"
            f"  {PROG} \"https://example.com\"\n"
            f"  {PROG} \"https://example.com\" -o code.svg --size 512\n"
            f"  echo \"text\" | {PROG} - --terminal"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("content", help="link or text to encode ('-' reads from stdin)")
    parser.add_argument("-o", "--output", help="output file or directory ('-' writes raw bytes to stdout); "
                                               "defaults to qr-<slug>.<format> in the current directory")
    parser.add_argument("-f", "--format", choices=FORMATS, help="output format (default: from -o extension, else png)")
    parser.add_argument("-s", "--size", type=int, default=DEFAULT_SIZE, help=f"target size in pixels (default: {DEFAULT_SIZE})")
    parser.add_argument("-e", "--error", choices=ERROR_LEVELS, default=DEFAULT_ERROR, type=str.upper,
                        help=f"error correction level (default: {DEFAULT_ERROR})")
    parser.add_argument("--fg", default=DEFAULT_FG, help=f"QR color as hex (default: {DEFAULT_FG})")
    parser.add_argument("--bg", default=DEFAULT_BG, help=f"background color as hex (default: {DEFAULT_BG})")
    parser.add_argument("--border", type=int, default=DEFAULT_BORDER, help=f"quiet zone in modules (default: {DEFAULT_BORDER})")
    parser.add_argument("-t", "--terminal", action="store_true", help="print the QR code in the terminal instead of saving a file")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON to stdout")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress progress messages")
    parser.add_argument("-v", "--verbose", action="store_true", help="show full tracebacks on errors")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.set_defaults(func=cmd_generate)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args) or EXIT_OK
    except CLIError as e:
        print(f"error: {e}", file=sys.stderr)
        return EXIT_ERROR
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return EXIT_INTERRUPTED
    except Exception as e:
        if getattr(args, "verbose", False):
            raise
        print(f"error: {e} (use -v for details)", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
