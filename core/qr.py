"""
Core QR code generation for Link to QR (used by the CLI).

The web UI renders QR codes client-side with qrcode.min.js; this module
mirrors the same options (size, error correction, colors) in Python using
`segno`, a pure-Python QR encoder with no further dependencies.
"""

import io
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

DEFAULT_SIZE = 384
DEFAULT_ERROR = "H"
DEFAULT_FG = "#000000"
DEFAULT_BG = "#ffffff"
DEFAULT_BORDER = 4
ERROR_LEVELS = ("L", "M", "Q", "H")
FORMATS = ("png", "svg")

_HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _segno():
    import segno  # imported lazily so callers that only need helpers stay fast

    return segno


def validate_color(value: str) -> str:
    """Accept #RGB / #RRGGBB hex colors (with or without '#'); return normalized '#rrggbb'."""
    color = value.strip()
    if not color.startswith("#"):
        color = f"#{color}"
    if not _HEX_COLOR.match(color):
        raise ValueError(f"Invalid color '{value}'. Use hex like #000000 or #fff.")
    if len(color) == 4:
        color = "#" + "".join(ch * 2 for ch in color[1:])
    return color.lower()


def slugify(text: str, max_len: int = 40) -> str:
    """Build a filesystem-friendly slug from QR content (e.g. a URL)."""
    cleaned = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", "", text.strip())
    cleaned = re.sub(r"^www\.", "", cleaned)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", cleaned).strip("-").lower()
    return slug[:max_len].rstrip("-") or "code"


def make_qr(text: str, error: str = DEFAULT_ERROR):
    """Encode text into a segno QR code object."""
    if not text:
        raise ValueError("QR content cannot be empty.")
    level = error.upper()
    if level not in ERROR_LEVELS:
        raise ValueError(f"Invalid error correction level '{error}'. Choose from {', '.join(ERROR_LEVELS)}.")
    return _segno().make(text, error=level.lower(), micro=False)


def scale_for_size(qr, size: int, border: int = DEFAULT_BORDER) -> int:
    """Largest integer module scale whose rendered width fits within `size` pixels (minimum 1)."""
    modules, _ = qr.symbol_size(scale=1, border=border)
    return max(1, size // modules)


def render_qr(
    text: str,
    fmt: str = "png",
    size: int = DEFAULT_SIZE,
    error: str = DEFAULT_ERROR,
    fg: str = DEFAULT_FG,
    bg: str = DEFAULT_BG,
    border: int = DEFAULT_BORDER,
) -> Dict[str, Any]:
    """
    Render a QR code to bytes.
    Returns {"data": bytes, "format", "size" (actual px), "version", "error", "modules"}.
    """
    fmt = fmt.lower()
    if fmt not in FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from {', '.join(FORMATS)}.")
    if size < 21:
        raise ValueError("Size must be at least 21 pixels.")
    if border < 0:
        raise ValueError("Border cannot be negative.")

    qr = make_qr(text, error)
    scale = scale_for_size(qr, size, border)
    buffer = io.BytesIO()
    qr.save(buffer, kind=fmt, scale=scale, dark=validate_color(fg), light=validate_color(bg), border=border)
    actual, _ = qr.symbol_size(scale=scale, border=border)
    return {
        "data": buffer.getvalue(),
        "format": fmt,
        "size": actual,
        "version": qr.version,
        "error": qr.error.upper() if qr.error else error.upper(),
        "modules": qr.symbol_size(scale=1, border=0)[0],
    }


def save_qr(text: str, output_path: Union[str, Path], fmt: Optional[str] = None, **options) -> Dict[str, Any]:
    """Render a QR code and write it to output_path. Format is inferred from the extension if not given."""
    path = Path(output_path)
    fmt = (fmt or path.suffix.lstrip(".") or "png").lower()
    result = render_qr(text, fmt=fmt, **options)
    path.write_bytes(result.pop("data"))
    result["output"] = str(path.resolve())
    result["bytes"] = path.stat().st_size
    return result


def terminal_qr(text: str, error: str = DEFAULT_ERROR, border: int = 2) -> str:
    """Render a QR code as compact Unicode block art for terminal display."""
    qr = make_qr(text, error)
    out = io.StringIO()
    qr.terminal(out=out, compact=True, border=border)
    return out.getvalue()
