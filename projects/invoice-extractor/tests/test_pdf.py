"""Reading the text layer, and refusing to guess when there isn't one."""

import pytest
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from invoice_extractor.pdf import NoTextLayer, pdf_to_text


def test_reads_a_real_invoice(samples_dir):
    text = pdf_to_text(samples_dir / "invoice_clean.pdf")
    assert "GOS-2026-0412" in text
    assert "Gulf Office Supplies WLL" in text
    assert "420.00" in text


def test_scanned_pdf_raises_instead_of_returning_nothing(tmp_path):
    """An empty string handed to the model invents an invoice. Fail loudly."""
    blank = tmp_path / "scan.pdf"
    canvas.Canvas(str(blank), pagesize=A4).save()
    with pytest.raises(NoTextLayer, match="OCR"):
        pdf_to_text(blank)


def test_text_is_truncated_to_the_limit(samples_dir):
    assert len(pdf_to_text(samples_dir / "invoice_clean.pdf", max_chars=50)) == 50
