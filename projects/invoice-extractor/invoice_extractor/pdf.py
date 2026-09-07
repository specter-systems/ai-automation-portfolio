"""PDF to text.

Deliberately dumb: pull the text layer and hand it on. If a PDF has no text
layer it is a scan, and this raises rather than silently returning "" and
letting the model hallucinate an invoice out of nothing.
"""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

MAX_CHARS = 40_000


class NoTextLayer(RuntimeError):
    """Raised for image-only PDFs, which need OCR before they can be read."""


def pdf_to_text(path: str | Path, *, max_chars: int = MAX_CHARS) -> str:
    reader = PdfReader(str(path))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    if not text.strip():
        raise NoTextLayer(
            f"{Path(path).name} has no extractable text. It is probably a scan — "
            "run it through OCR first."
        )
    return text[:max_chars]
