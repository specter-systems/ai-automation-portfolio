"""Command line entry point.

    invoice-extract samples/*.pdf --csv out.csv --approval-threshold 5000

Exit code is 1 if any invoice raised an ERROR, so this drops straight into a
cron job or a CI step without extra plumbing.
"""

from __future__ import annotations

import argparse
import csv
import sys
from decimal import Decimal
from pathlib import Path

from .checks import check_invoice, find_duplicates
from .extract import extract_invoice
from .models import Invoice
from .pdf import NoTextLayer, pdf_to_text

CSV_COLUMNS = [
    "source_file", "vendor", "invoice_number", "invoice_date", "due_date",
    "currency", "subtotal", "tax", "total", "line_item_count", "status",
]


def _row(inv: Invoice, status: str) -> dict:
    return {
        "source_file": inv.source_file or "",
        "vendor": inv.vendor or "",
        "invoice_number": inv.invoice_number or "",
        "invoice_date": inv.invoice_date or "",
        "due_date": inv.due_date or "",
        "currency": inv.currency or "",
        "subtotal": inv.subtotal if inv.subtotal is not None else "",
        "tax": inv.tax if inv.tax is not None else "",
        "total": inv.total if inv.total is not None else "",
        "line_item_count": len(inv.line_items),
        "status": status,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="invoice-extract", description=__doc__)
    ap.add_argument("files", nargs="+", type=Path, help="PDF invoices to read.")
    ap.add_argument("--csv", type=Path, help="Write a row per invoice here.")
    ap.add_argument("--approval-threshold", type=Decimal, default=None,
                    help="Flag any invoice with a total above this.")
    args = ap.parse_args(argv)

    invoices: list[Invoice] = []
    findings_by_file: dict[str, list] = {}
    failed = False

    for path in args.files:
        try:
            invoice = extract_invoice(pdf_to_text(path), source_file=path.name)
        except NoTextLayer as exc:
            print(f"{path.name}: SKIPPED — {exc}", file=sys.stderr)
            failed = True
            continue
        except Exception as exc:  # noqa: BLE001 - one bad file must not kill the batch
            print(f"{path.name}: FAILED — {exc}", file=sys.stderr)
            failed = True
            continue
        invoices.append(invoice)
        findings_by_file[path.name] = check_invoice(
            invoice, approval_threshold=args.approval_threshold
        )

    for finding in find_duplicates(invoices):
        findings_by_file.setdefault("batch", []).append(finding)

    for name, findings in findings_by_file.items():
        if not findings:
            print(f"{name}: clean")
            continue
        print(f"{name}:")
        for f in findings:
            print(f"  {f}")

    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for inv in invoices:
                errors = [f for f in findings_by_file.get(inv.source_file or "", [])
                          if f.severity == "ERROR"]
                writer.writerow(_row(inv, "REVIEW" if errors else "OK"))
        print(f"\nWrote {len(invoices)} row(s) to {args.csv}")

    has_error = any(f.severity == "ERROR" for fs in findings_by_file.values() for f in fs)
    return 1 if (has_error or failed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
