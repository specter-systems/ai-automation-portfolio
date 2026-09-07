"""Generate sample invoice PDFs, including one that is deliberately wrong.

    python samples/make_sample_invoices.py

The broken one exists so you can watch the checks fire on a real file rather
than taking my word for it.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent


def draw(path: Path, rows: list[tuple[str, str, str, str]], *, number: str,
         subtotal: str, tax: str, total: str, issued: str, due: str) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 70

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Gulf Office Supplies WLL")
    c.setFont("Helvetica", 10)
    y -= 18
    c.drawString(50, y, "Salwa Road, Doha, Qatar")

    y -= 40
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "TAX INVOICE")
    c.setFont("Helvetica", 10)
    for label, value in (("Invoice number:", number), ("Invoice date:", issued),
                         ("Due date:", due), ("Currency:", "QAR")):
        y -= 16
        c.drawString(50, y, label)
        c.drawString(160, y, value)

    y -= 32
    c.setFont("Helvetica-Bold", 10)
    for x, head in ((50, "Description"), (300, "Qty"), (360, "Unit price"), (460, "Amount")):
        c.drawString(x, y, head)
    c.setFont("Helvetica", 10)
    for desc, qty, unit, amount in rows:
        y -= 16
        for x, val in ((50, desc), (300, qty), (360, unit), (460, amount)):
            c.drawString(x, y, val)

    y -= 30
    c.setFont("Helvetica", 10)
    for label, value in (("Subtotal", subtotal), ("Tax", tax)):
        c.drawString(360, y, label)
        c.drawString(460, y, value)
        y -= 16
    c.setFont("Helvetica-Bold", 11)
    c.drawString(360, y, "Total")
    c.drawString(460, y, total)
    c.save()


def main() -> None:
    draw(
        HERE / "invoice_clean.pdf",
        [("A4 paper, 80gsm, box", "4", "45.00", "180.00"),
         ("Whiteboard markers, pack of 12", "3", "30.00", "90.00"),
         ("Desk organiser", "2", "65.00", "130.00")],
        number="GOS-2026-0412", subtotal="400.00", tax="20.00", total="420.00",
        issued="2026-08-14", due="2026-09-13",
    )
    # Line two reads 90.00 but 3 x 25.00 is 75.00, and the total is 100 short.
    draw(
        HERE / "invoice_broken.pdf",
        [("A4 paper, 80gsm, box", "4", "45.00", "180.00"),
         ("Whiteboard markers, pack of 12", "3", "25.00", "90.00"),
         ("Desk organiser", "2", "65.00", "130.00")],
        number="GOS-2026-0413", subtotal="400.00", tax="20.00", total="320.00",
        issued="2026-08-15", due="2026-09-14",
    )
    print("Wrote invoice_clean.pdf and invoice_broken.pdf")


if __name__ == "__main__":
    main()
