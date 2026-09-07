"""Deterministic checks run *after* extraction.

This is the part that matters. A language model reading a scanned invoice is
very good and occasionally confidently wrong, so nothing it returns is
trusted on arithmetic. Every number it produces is re-checked here in plain
Python, and anything that fails goes to a human instead of to the ledger.

Severity is the routing decision:
    ERROR  -> do not post, needs a person
    WARN   -> post, but flag for review
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Literal

from .models import Invoice

Severity = Literal["ERROR", "WARN"]

# Invoices are rounded to the minor unit; allow one unit of slack so a
# legitimate rounding difference is not reported as a mismatch.
TOLERANCE = Decimal("0.01")


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    message: str

    def __str__(self) -> str:
        return f"[{self.severity}] {self.code}: {self.message}"


def check_invoice(inv: Invoice, *, today: date | None = None,
                  approval_threshold: Decimal | None = None) -> list[Finding]:
    """Return every problem found on one invoice. Empty list means clean."""
    today = today or date.today()
    out: list[Finding] = []

    for field in ("vendor", "invoice_number", "invoice_date", "total"):
        if getattr(inv, field) in (None, ""):
            out.append(Finding("MISSING_FIELD", "ERROR", f"No {field.replace('_', ' ')} found."))

    if not inv.line_items:
        out.append(Finding("NO_LINE_ITEMS", "WARN", "No line items were extracted."))

    for li in inv.line_items:
        if li.quantity < 0 or li.unit_price < 0:
            out.append(Finding("NEGATIVE_VALUE", "ERROR",
                               f"Negative quantity or price on '{li.description}'."))
        expected = (li.quantity * li.unit_price).quantize(Decimal("0.01"))
        if abs(expected - li.amount) > TOLERANCE:
            out.append(Finding("LINE_MATH", "ERROR",
                               f"'{li.description}': {li.quantity} x {li.unit_price} "
                               f"= {expected}, but line reads {li.amount}."))

    if inv.subtotal is not None and inv.line_items:
        if abs(inv.line_item_total - inv.subtotal) > TOLERANCE:
            out.append(Finding("SUBTOTAL_MISMATCH", "ERROR",
                               f"Line items sum to {inv.line_item_total}, "
                               f"subtotal reads {inv.subtotal}."))

    if inv.total is not None and inv.subtotal is not None:
        expected = inv.subtotal + (inv.tax or Decimal("0"))
        if abs(expected - inv.total) > TOLERANCE:
            out.append(Finding("TOTAL_MISMATCH", "ERROR",
                               f"Subtotal plus tax is {expected}, total reads {inv.total}."))

    if inv.invoice_date and inv.invoice_date > today:
        out.append(Finding("FUTURE_DATE", "ERROR",
                           f"Invoice is dated {inv.invoice_date}, which is in the future."))

    if inv.invoice_date and inv.due_date and inv.due_date < inv.invoice_date:
        out.append(Finding("DUE_BEFORE_ISSUE", "WARN",
                           f"Due {inv.due_date} but issued {inv.invoice_date}."))

    if approval_threshold is not None and inv.total is not None:
        if inv.total > approval_threshold:
            out.append(Finding("NEEDS_APPROVAL", "WARN",
                               f"Total {inv.total} is above the {approval_threshold} threshold."))

    return out


def find_duplicates(invoices: Iterable[Invoice]) -> list[Finding]:
    """Catch the same invoice number arriving twice — the classic double payment."""
    seen: dict[str, str] = {}
    out: list[Finding] = []
    for inv in invoices:
        key = (inv.invoice_number or "").strip().upper()
        if not key:
            continue
        origin = f"{(inv.vendor or '?').strip().upper()}|{key}"
        if origin in seen:
            out.append(Finding("DUPLICATE_INVOICE", "ERROR",
                               f"Invoice {inv.invoice_number} from {inv.vendor} already seen "
                               f"in {seen[origin]}."))
        else:
            seen[origin] = inv.source_file or "an earlier file"
    return out
